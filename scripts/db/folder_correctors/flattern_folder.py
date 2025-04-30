import os
import shutil
from tqdm import tqdm

def flatten_subfolders_in_root(root_dir):
    # Csak a gyökér szintű mappákat vesszük célba
    root_level_dirs = [os.path.join(root_dir, d) for d in os.listdir(root_dir)
                       if os.path.isdir(os.path.join(root_dir, d))]

    for top_dir in tqdm(root_level_dirs, desc="Gyökérszintű mappák feldolgozása"):
        for root, dirs, files in os.walk(top_dir, topdown=False):
            for subdir in dirs:
                subdir_path = os.path.join(root, subdir)
                parent_path = os.path.dirname(subdir_path)

                # Mozgatjuk a fájlokat a szülőbe
                for item in os.listdir(subdir_path):
                    src = os.path.join(subdir_path, item)
                    dst = os.path.join(parent_path, item)

                    # Ha ütközés van, új név generálása
                    if os.path.exists(dst):
                        base, ext = os.path.splitext(item)
                        counter = 1
                        while True:
                            new_name = f"{base}_{counter}{ext}"
                            dst = os.path.join(parent_path, new_name)
                            if not os.path.exists(dst):
                                break
                            counter += 1

                    shutil.move(src, dst)

                # Ha az almappa kiürült, töröljük
                if not os.listdir(subdir_path):
                    os.rmdir(subdir_path)

if __name__ == "__main__":
    root_dir = os.getcwd()
    print(f"Gyökérkönyvtár: {root_dir}")
    flatten_subfolders_in_root(root_dir)
