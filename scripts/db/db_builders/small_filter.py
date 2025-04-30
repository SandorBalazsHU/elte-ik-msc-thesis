import os
import shutil
from tqdm import tqdm

# 🧮 Minimum képszám
min_size = 300

# 📁 Gyökérmappa és célmappa
root_path = r"D:\diplomamunka\CNN_DB\db\sorted_db"  # ⬅️ Állítsd be, ha más
small_target = os.path.join(root_path, "aa_small")

# 📂 Létrehozzuk a célmappát, ha nem létezne
os.makedirs(small_target, exist_ok=True)

# 📦 Összes almappa beolvasása
subfolders = [os.path.join(root_path, d) for d in os.listdir(root_path)
              if os.path.isdir(os.path.join(root_path, d)) and d != "aa_small"]

# 📋 Kiválasztjuk az áthelyezendő mappákat
folders_to_move = []
for folder in subfolders:
    num_files = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
    if num_files < min_size:
        folders_to_move.append(folder)

print(f"🔍 {len(folders_to_move)} mappa kerül áthelyezésre az 'aa_small' mappába.")

# 🚚 Áthelyezés progress bar-ral
for folder in tqdm(folders_to_move, desc="📂 Mappák áthelyezése"):
    folder_name = os.path.basename(folder)
    target_path = os.path.join(small_target, folder_name)

    if os.path.exists(target_path):
        print(f"⚠️ Figyelem: {target_path} már létezik, kihagyva.")
        continue

    shutil.move(folder, target_path)

print("✅ Áthelyezés kész.")
