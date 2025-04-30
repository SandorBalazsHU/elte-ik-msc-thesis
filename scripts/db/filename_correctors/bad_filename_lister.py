import os
import re

# 📁 Gyökérkönyvtár, amit vizsgálni szeretnél
root_dir = r'D:\diplomamunka\CNN_DB\db\sorted_db'  # ⬅️ Állítsd be

# 🧪 MD5 pattern (32 kisbetűs hex karakter + .jpg)
md5_pattern = re.compile(r'^[a-f0-9]{32}\.jpg$')

invalid_files = []

# 🔍 Rekurzív bejárás
for root, _, files in os.walk(root_dir):
    for file in files:
        file_path = os.path.join(root, file)

        # Csak .jpg fájlokat vizsgálunk
        if not file.lower().endswith('.jpg'):
            invalid_files.append(file_path)
            continue

        # MD5-nek megfelelő fájlnév?
        if not md5_pattern.match(file):
            invalid_files.append(file_path)

# 📋 Eredmény
if invalid_files:
    print(f"⚠️ Nem szabványos fájlnevek száma: {len(invalid_files)}\n")
    for path in invalid_files:
        print("  -", path)
else:
    print("✅ Minden fájlnév MD5-hash formátumú.")


