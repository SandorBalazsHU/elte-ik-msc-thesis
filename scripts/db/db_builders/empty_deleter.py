import os
from tqdm import tqdm

# 📁 Állítsd be azt a mappát, ahol a kategóriáid vannak
root_path = r"D:\diplomamunka\CNN_DB\db\sorted_db"  # ⬅️ Itt add meg a kategóriamappáid gyökerét

def delete_empty_folders(path):
    removed = 0
    subfolders = [os.path.join(path, d) for d in os.listdir(path)
                  if os.path.isdir(os.path.join(path, d))]

    for folder in tqdm(subfolders, desc="🗑️ Üres mappák törlése"):
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        if len(files) == 0:
            try:
                os.rmdir(folder)
                removed += 1
            except Exception as e:
                print(f"Hiba a törlésnél: {folder} – {e}")

    print(f"✅ Törölt mappák száma: {removed}")

# 🚀 Futtatás
delete_empty_folders(root_path)
