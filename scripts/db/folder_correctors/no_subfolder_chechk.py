import os

# 📁 Ellenőrizendő gyökérmappa
root_dir = r'D:\diplomamunka\CNN_DB\db\sorted_db'

invalid_folders = []

# 📂 Minden közvetlen almappa vizsgálata
for folder_name in os.listdir(root_dir):
    folder_path = os.path.join(root_dir, folder_name)
    if not os.path.isdir(folder_path):
        continue  # fájl, nem mappa

    # Keresünk almappát benne
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            invalid_folders.append(folder_path)
            break  # elég egy almappa is

# 📋 Eredmény
if invalid_folders:
    print(f"⚠️ Ezek a mappák tartalmaznak további almappákat ({len(invalid_folders)}):\n")
    for path in invalid_folders:
        print("  -", path)
else:
    print("✅ Minden mappa pontosan 1 szint mély. Nincs almappa sehol.")
