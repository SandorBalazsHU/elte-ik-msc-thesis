import os
import shutil
import subprocess
import sys

def main():
    # A szkript könyvtára
    base_dir = os.path.dirname(os.path.abspath(__file__))
    convert_bat = os.path.join(base_dir, 'convert.bat')

    if not os.path.isfile(convert_bat):
        print(f"[ERROR] 'convert.bat' nincs megtalálható a {base_dir} könyvtárban.")
        sys.exit(1)

    # 1) Mappatérkép készítése (előzetesen, hogy a későbbi 'resized' mappákat ne találja meg)
    directories = []
    for root, dirs, _ in os.walk(base_dir):
        # Ha a mappa neve 'resized', ugorjuk át
        if os.path.basename(root).lower() == 'resized':
            continue
        directories.append(root)

    print(f"[INFO] Felderített {len(directories)} könyvtárat.")

    # 2) convert.bat másolása minden mappába
    for d in directories:
        dest = os.path.join(d, 'convert.bat')
        try:
            shutil.copy2(convert_bat, dest)
            print(f"[COPY] {dest}")
        except Exception as e:
            print(f"[ERROR] Nem sikerült másolni ide: {d} ({e})")

    # 3) A batch fájl futtatása minden mappában
    for d in directories:
        bat_path = os.path.join(d, 'convert.bat')
        print(f"[RUN] {bat_path}")
        # Windows-on futtatáshoz
        subprocess.run(['cmd', '/c', bat_path], cwd=d)

if __name__ == '__main__':
    main()