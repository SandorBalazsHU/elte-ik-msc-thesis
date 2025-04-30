import os
import shutil
import sys

def main():
    # A szkript könyvtára lesz a gyökér
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Célmappa a full_resized
    full_resized_dir = os.path.join(base_dir, 'full_resized')
    if not os.path.exists(full_resized_dir):
        os.makedirs(full_resized_dir)
        print(f"[INFO] Létrehozva: {full_resized_dir}")
    else:
        print(f"[INFO] Már létezik: {full_resized_dir}")

    # 1) Keressük meg az összes 'resized' mappát
    resized_dirs = []
    for root, dirs, files in os.walk(base_dir):
        # ha a root mappa neve 'resized', vegyük fel
        if os.path.basename(root).lower() == 'resized':
            resized_dirs.append(root)

    print(f"[INFO] {len(resized_dirs)} darab 'resized' mappa található.")

    # 2) Másolás full_resized-be, névütközésnél kihagyjuk
    for rd in resized_dirs:
        print(f"[PROCESS] {rd} tartalmának másolása...")
        for fname in os.listdir(rd):
            src = os.path.join(rd, fname)
            dst = os.path.join(full_resized_dir, fname)

            # csak fájlokat másolunk
            if not os.path.isfile(src):
                continue

            if os.path.exists(dst):
                print(f"  [SKIP] Már létezik: {fname}")
                continue

            try:
                shutil.copy2(src, dst)
                print(f"  [COPY] {fname}")
            except Exception as e:
                print(f"  [ERROR] Nem sikerült másolni {fname}: {e}")

    print("[DONE] Minden 'resized' mappa feldolgozva.")

if __name__ == '__main__':
    main()
