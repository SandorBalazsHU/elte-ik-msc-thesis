import os
from collections import defaultdict
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from rich.console import Console
from rich.table import Table
from rich import box

# 📋 Konfiguráció
min_size = 300
db_root = r"D:\diplomamunka\CNN_DB\db"

# 📁 Konzolos mappaválasztás
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

# 📊 Képszámok összesítése
def count_files_by_folder(path):
    folder_file_count = defaultdict(int)
    total_file_count = 0
    subfolders = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    print(f"📂 Talált almappák száma: {len(subfolders)}")

    for folder in tqdm(subfolders, desc="📦 Fájlok számolása"):
        num_files = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
        folder_file_count[os.path.basename(folder)] = num_files
        total_file_count += num_files

    return total_file_count, dict(sorted(folder_file_count.items(), key=lambda x: x[1], reverse=True))

# 📋 Rich táblás kiírás
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

# 📈 Top 30 diagram
def plot_top_n_folders_highlighted(data, n=30, min_size=300):
    top_items = list(data.items())[:n]
    folders, counts = zip(*top_items)

    colors = ['red' if c == 0 else 'gold' if c < min_size else 'steelblue' for c in counts]

    plt.figure(figsize=(10, 6))
    plt.barh(folders, counts, color=colors)
    plt.xlabel("Fájlok száma")
    plt.title(f"Top {n} kategória fájlszám szerint (min. kiemelés: < {min_size})")
    plt.tight_layout()
    plt.gca().invert_yaxis()
    plt.show()

# 📈 Histogram + bővített statisztikák
def plot_histogram_and_stats(data, min_size):
    values = list(data.values())
    if not values:
        print("⚠️ Nincs adat.")
        return

    # 📈 Histogram
    plt.figure(figsize=(10, 5))
    plt.hist(values, bins=30, color='skyblue', edgecolor='black')
    plt.axvline(np.mean(values), color='green', linestyle='dashed', linewidth=1, label='Átlag')
    plt.axvline(np.median(values), color='orange', linestyle='dashed', linewidth=1, label='Medián')
    plt.title("📉 Kategóriák eloszlása")
    plt.xlabel("Fájlok száma")
    plt.ylabel("Kategóriák száma")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # 📊 Statisztikák
    mean_val = np.mean(values)
    median_val = np.median(values)
    stddev_val = np.std(values)
    skewness = stats.skew(values)
    gini = gini_index(values)
    entropy = stats.entropy(values)
    empty = sum(1 for v in values if v == 0)
    small = sum(1 for v in values if v < min_size)

    print("\n📊 Bővített statisztikai összefoglaló:")
    print(f"  🧮 Átlag: {mean_val:.2f}")
    print(f"  📍 Medián: {median_val}")
    print(f"  📉 Szórás: {stddev_val:.2f}")
    print(f"  🔀 Aszimmetria (skewness): {skewness:.2f}")
    print(f"  ⚖️ Gini-index: {gini:.4f}")
    print(f"  🔢 Entropia: {entropy:.4f}")
    print(f"  ❌ Üres kategóriák száma: {empty}")
    print(f"  ⚠️ {min_size} alatti kategóriák száma: {small}")

# ⚖️ Gini-index számítása
def gini_index(values):
    sorted_vals = np.sort(np.array(values))
    n = len(sorted_vals)
    if n == 0 or sorted_vals[-1] == 0:
        return 0
    cumvals = np.cumsum(sorted_vals)
    return (n + 1 - 2 * np.sum(cumvals) / cumvals[-1]) / n

# ▶️ Futtatás
selected_path = choose_subfolder(db_root)
total, folder_counts = count_files_by_folder(selected_path)
display_rich_table(folder_counts, total)
plot_top_n_folders_highlighted(folder_counts, n=30, min_size=min_size)
plot_histogram_and_stats(folder_counts, min_size)

