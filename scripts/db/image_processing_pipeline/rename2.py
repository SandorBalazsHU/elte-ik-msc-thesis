import os
import random
import string
import hashlib
from tqdm import tqdm

# --- Beállítások ---
NAME_LENGTH = 25                        # Változtatható névhossz (pl. 20–25)
USE_MD5 = True                          # Ha True, az új név az MD5 hash lesz
TARGET_EXTENSIONS = {'.jpg', '.jpeg', '.png'}  # Feldolgozandó kiterjesztések

# A szkript könyvtára lesz az alapértelmezett gyökér
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Random név generálása ---
def generate_random_name(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

# --- MD5 hash generálása ---
def generate_md5(filepath):
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# --- Könyvtárak felderítése ---
directories = []
for root, dirs, _ in os.walk(BASE_DIR):
    directories.append(root)

print(f"[INFO] Felderített könyvtárak száma: {len(directories)}")
for d in directories:
    print(f"  - {os.path.relpath(d, BASE_DIR)}")

# --- Minden könyvtár feldolgozása ---
for FOLDER in directories:
    # Fájlok listázása a célkiterjesztésekkel
    files = [
        f for f in os.listdir(FOLDER)
        if os.path.isfile(os.path.join(FOLDER, f))
           and os.path.splitext(f)[1].lower() in TARGET_EXTENSIONS
    ]

    if not files:
        print(f"[INFO] {os.path.relpath(FOLDER, BASE_DIR)}: nincs megfelelő fájl.")
        continue

    print(f"[INFO] {os.path.relpath(FOLDER, BASE_DIR)}: {len(files)} fájl átnevezése...")

    for filename in tqdm(files, desc=f"Renaming in {os.path.relpath(FOLDER, BASE_DIR)}"):
        full_path = os.path.join(FOLDER, filename)
        ext = os.path.splitext(filename)[1].lower()

        # Új név generálása
        if USE_MD5:
            newname = generate_md5(full_path)
        else:
            newname = generate_random_name(NAME_LENGTH)

        new_filename = f"{newname}{ext}"
        new_path = os.path.join(FOLDER, new_filename)

        # Ütközés elkerülése
        while os.path.exists(new_path):
            if USE_MD5:
                newname += '_1'
            else:
                newname = generate_random_name(NAME_LENGTH)
            new_filename = f"{newname}{ext}"
            new_path = os.path.join(FOLDER, new_filename)

        os.rename(full_path, new_path)

    print(f"[DONE] {os.path.relpath(FOLDER, BASE_DIR)}: minden fájl átnevezve.")

print("[ALL DONE] Az összes könyvtárban végezve.") 
