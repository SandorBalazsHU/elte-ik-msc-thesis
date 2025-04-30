import os
import re
import uuid

# 📁 Gyökérkönyvtár
root_dir = r'D:\diplomamunka\CNN_DB\db\sorted_db'  # ⬅️ Állítsd be

# ✅ Helyes MD5 minta (kisbetűs, 32 karakter, .jpg végződés)
md5_pattern = re.compile(r'^[a-f0-9]{32}\.jpg$')

# 📋 Nyilvántartás az új nevek ütközés elkerüléséhez
used_names = set()

# 🛠️ Már létező nevek előre betöltése (ütközés elkerülése)
for root, _, files in os.walk(root_dir):
    for file in files:
        if file.lower().endswith('.jpg'):
            used_names.add(file.lower())

# 🔄 Fájlok bejárása és átnevezés
renamed_files = []
for root, _, files in os.walk(root_dir):
    for file in files:
        if not file.lower().endswith('.jpg'):
            continue

        if md5_pattern.match(file):
            continue  # már jó név

        old_path = os.path.join(root, file)

        # 🔁 Új MD5-szerű név generálása
        while True:
            new_hash = uuid.uuid4().hex  # 32 karakteres hex (kisbetűs)
            new_filename = f"{new_hash}.jpg"
            if new_filename not in used_names:
                break

        new_path = os.path.join(root, new_filename)
        os.rename(old_path, new_path)
        used_names.add(new_filename)
        renamed_files.append((file, new_filename))

# 📋 Eredmény kiírása
if renamed_files:
    print(f"✅ {len(renamed_files)} fájlt neveztünk át:")
    for old, new in renamed_files:
        print(f"  - {old} → {new}")
else:
    print("✅ Minden fájlnév szabványos volt. Nem történt módosítás.")

