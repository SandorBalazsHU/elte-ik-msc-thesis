import os
import shutil
from tqdm import tqdm

# 📁 Célmappa (ez tartalmazza az almappákat)
small_folder = r"D:\diplomamunka\CNN_DB\db\unsorted_db"  # ⬅️ Frissítsd, ha kell

# 📂 Almappák kilistázása
subfolders = [os.path.join(small_folder, d) for d in os.listdir(small_folder)
              if os.path.isdir(os.path.join(small_folder, d))]

print(f"📂 Talált almappák: {len(subfolders)}")

# 🔄 Áthelyezés és törlés
for folder in tqdm(subfolders, desc="📁 Almappák feldolgozása"):
    for file_name in os.listdir(folder):
        src_file = os.path.join(folder, file_name)
        dest_file = os.path.join(small_folder, file_name)

        # Csak fájlokat mozgatunk
        if os.path.isfile(src_file):
            if os.path.exists(dest_file):
                print(f"⚠️ Ütközés: {dest_file} már létezik. Kihagyva.")
                continue
            shutil.move(src_file, dest_file)

    # Ellenőrzés: maradt-e valami?
    if not os.listdir(folder):  # Üres?
        os.rmdir(folder)
        print(f"🗑️ Törölve: {folder}")
    else:
        print(f"⚠️ Nem üres, nem töröltem: {folder}")

print("✅ Művelet kész.")
