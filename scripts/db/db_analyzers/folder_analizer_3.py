import os
import hashlib
from collections import defaultdict
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime

min_size = 300
valid_exts = ('.jpg', '.jpeg')
db_root = r"D:\diplomamunka\CNN_DB\db"

def choose_subfolder(base_path):
    subfolders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    print("📂 Elérhető mappák a 'db' könyvtárban:")
    for i, d in enumerate(subfolders, 1):
        print(f"  {i}. {d}")
    while True:
        try:
            choice = int(input("🔎 Add meg a kiválasztott mappa sorszámát: "))
            if 1 <= choice <= len(subfolders):
                return os.path.join(base_path, subfolders[choice - 1])
            else:
                print("⚠️ Érvénytelen választás. Próbáld újra.")
        except ValueError:
            print("⚠️ Kérlek számot adj meg.")

def detect_structure(path):
    subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    if not subdirs:
        return "flat"
    elif set(["train", "val", "test"]).issubset(set(subdirs)):
        return "split"
    else:
        return "structured"

def gini_index(values):
    sorted_vals = np.sort(np.array(values))
    n = len(sorted_vals)
    if n == 0 or sorted_vals[-1] == 0:
        return 0
    cumvals = np.cumsum(sorted_vals)
    return (n + 1 - 2 * np.sum(cumvals) / cumvals[-1]) / n

def display_rich_table(folder_counts, total):
    console = Console()
    table = Table(title=f"Kategóriaeloszlás – Összesen {total} kép", box=box.SIMPLE)
    table.add_column("📁 Mappa", style="bold")
    table.add_column("🧮 Képszám", justify="right")

    for folder, count in folder_counts.items():
        if count == 0:
            table.add_row(folder, str(count), style="bold red")
        elif count < min_size:
            table.add_row(folder, str(count), style="yellow")
        else:
            table.add_row(folder, str(count))
    console.print(table)

def analyze_flat(path):
    files = [f for f in os.listdir(path) if f.lower().endswith(valid_exts)]
    total = len(files)
    print(f"\n📸 Összes kép: {total}")

    # Módosítási idők gyűjtése
    mod_times = []
    hashes = set()
    dupes = 0
    for file in tqdm(files, desc="⏱️ Dátumok és duplikáció ellenőrzése"):
        full_path = os.path.join(path, file)
        try:
            mod_time = os.path.getmtime(full_path)
            mod_times.append(datetime.fromtimestamp(mod_time))

            # MD5 hash ellenőrzés
            with open(full_path, 'rb') as f:
                md5 = hashlib.md5(f.read()).hexdigest()
                if md5 in hashes:
                    dupes += 1
                else:
                    hashes.add(md5)
        except:
            continue

    print(f"🔁 Duplikált képek száma: {dupes}")
    if mod_times:
        plt.hist([dt.date() for dt in mod_times], bins=30, color='skyblue', edgecolor='black')
        plt.title("🗓️ Képek létrehozási/módosítási dátum szerinti eloszlása")
        plt.xlabel("Dátum")
        plt.ylabel("Képek száma")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def analyze_structured(path):
    folder_counts = {}
    total = 0
    for folder in tqdm(os.listdir(path), desc="📦 Kategóriák feldolgozása"):
        full_path = os.path.join(path, folder)
        if os.path.isdir(full_path):
            count = len([f for f in os.listdir(full_path) if f.lower().endswith(valid_exts)])
            folder_counts[folder] = count
            total += count

    display_rich_table(folder_counts, total)
    values = list(folder_counts.values())
    if not values:
        print("⚠️ Nincs adat.")
        return

    plt.barh(list(folder_counts.keys())[:30], list(folder_counts.values())[:30], color='steelblue')
    plt.gca().invert_yaxis()
    plt.xlabel("Képszám")
    plt.title("Top 30 kategória képszám szerint")
    plt.tight_layout()
    plt.show()

    plt.hist(values, bins=30, color='skyblue', edgecolor='black')
    plt.axvline(np.mean(values), color='green', linestyle='--', label='Átlag')
    plt.axvline(np.median(values), color='orange', linestyle='--', label='Medián')
    plt.title("📉 Kategóriák képszám szerinti eloszlása")
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.boxplot(values, vert=False)
    plt.title("📦 Kategóriaméret szórás (boxplot)")
    plt.tight_layout()
    plt.show()

    print("\n📊 Statisztikai összefoglaló:")
    print(f"  🧮 Átlag: {np.mean(values):.2f}")
    print(f"  📍 Medián: {np.median(values)}")
    print(f"  📉 Szórás: {np.std(values):.2f}")
    print(f"  🔀 Aszimmetria (skewness): {stats.skew(values):.2f}")
    print(f"  ⚖️ Gini-index: {gini_index(values):.4f}")
    print(f"  🔢 Entrópia: {stats.entropy(values):.4f}")

def analyze_split(path):
    split_counts = defaultdict(lambda: defaultdict(int))
    total = 0
    for split in ["train", "val", "test"]:
        split_path = os.path.join(path, split)
        if not os.path.exists(split_path):
            continue
        for folder in os.listdir(split_path):
            full_path = os.path.join(split_path, folder)
            if os.path.isdir(full_path):
                count = len([f for f in os.listdir(full_path) if f.lower().endswith(valid_exts)])
                split_counts[split][folder] = count
                total += count

    # Összesítés pie chart
    total_split = {k: sum(v.values()) for k, v in split_counts.items()}
    plt.pie(total_split.values(), labels=total_split.keys(), autopct='%1.1f%%')
    plt.title("🧪 Train/Val/Test megoszlás")
    plt.tight_layout()
    plt.show()

    # Bar chart split szerint
    plt.bar(total_split.keys(), total_split.values(), color='lightcoral')
    plt.title("Train / Val / Test képszám összehasonlítása")
    plt.tight_layout()
    plt.show()

    # Boxplot per split
    for split in split_counts:
        values = list(split_counts[split].values())
        plt.boxplot(values, vert=False)
        plt.title(f"📦 {split} halmaz kategóriaméret szórás")
        plt.tight_layout()
        plt.show()

    # Heatmap-like mátrix split-kategória
    all_categories = sorted({cat for split in split_counts.values() for cat in split})
    matrix = []
    for cat in all_categories:
        row = []
        for split in ["train", "val", "test"]:
            row.append(split_counts[split].get(cat, 0))
        matrix.append(row)
    matrix = np.array(matrix)
    plt.imshow(matrix, aspect='auto', cmap='YlGnBu')
    plt.colorbar(label='Képszám')
    plt.xticks(ticks=range(3), labels=['train', 'val', 'test'])
    plt.yticks(ticks=range(len(all_categories)), labels=all_categories)
    plt.title("📊 Split vs Kategória mátrix")
    plt.tight_layout()
    plt.show()

    print("\n📊 Underrepresentation vizsgálat:")
    for cat in all_categories:
        missing = [s for s in ["train", "val", "test"] if split_counts[s].get(cat, 0) == 0]
        if missing:
            print(f"  ⚠️ Kategória '{cat}' hiányzik itt: {', '.join(missing)}")

# ▶️ Futtatás
selected_path = choose_subfolder(db_root)
structure = detect_structure(selected_path)
print(f"🧠 Detektált struktúra: {structure}")

if structure == "flat":
    analyze_flat(selected_path)
elif structure == "structured":
    analyze_structured(selected_path)
elif structure == "split":
    analyze_split(selected_path)
