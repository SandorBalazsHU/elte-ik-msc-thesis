import os
from collections import defaultdict
from tqdm import tqdm
import matplotlib.pyplot as plt

# 🔧 Állítható minimum kategóriaméret
min_size = 300

# 📁 Elemzendő mappa
root_path = r"D:\diplomamunka\CNN_DB\db\sorted_db"  # ⬅️ Állítsd be

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

# 📊 Elemzés
total, folder_counts = count_files_by_folder(root_path)

# 📋 Formázott, színezett kiírás
from rich.console import Console
from rich.table import Table
from rich import box

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

# 📈 Színes diagram (csak top 30)
def plot_top_n_folders_highlighted(data, n=30, min_size=300):
    top_items = list(data.items())[:n]
    folders, counts = zip(*top_items)

    colors = []
    for c in counts:
        if c == 0:
            colors.append('red')
        elif c < min_size:
            colors.append('gold')
        else:
            colors.append('steelblue')

    plt.figure(figsize=(10, 6))
    plt.barh(folders, counts, color=colors)
    plt.xlabel("Fájlok száma")
    plt.title(f"Top {n} kategória fájlszám szerint (min. kiemelés: < {min_size})")
    plt.tight_layout()
    plt.gca().invert_yaxis()
    plt.show()

plot_top_n_folders_highlighted(folder_counts, n=30, min_size=min_size)
