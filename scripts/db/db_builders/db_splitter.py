import os
import shutil
import random
from glob import glob
from tqdm import tqdm

# 📁 Elérési utak
input_root = r'D:\diplomamunka\CNN_DB\db\imagenet_sorted_db'         # Forrás (meglévő, érintetlen marad)
output_root = r'D:\diplomamunka\CNN_DB\db\imagenet_splitted_db'      # Cél (újonnan létrejövő)
splits = ['train', 'val', 'test']
ratios = [0.8, 0.1, 0.1]  # ⬅️ Állítható, ha szeretnéd

# 📂 Létrehozzuk az output mappákat
for split in splits:
    os.makedirs(os.path.join(output_root, split), exist_ok=True)

# 📋 Kategóriák kilistázása
categories = [d for d in os.listdir(input_root)
              if os.path.isdir(os.path.join(input_root, d))]

print(f"📁 Kategóriák száma: {len(categories)}")

for category in tqdm(categories, desc="📦 Kategóriák feldolgozása"):
    src_folder = os.path.join(input_root, category)
    images = glob(os.path.join(src_folder, '*'))
    random.shuffle(images)

    n_total = len(images)
    n_train = int(n_total * ratios[0])
    n_val = int(n_total * ratios[1])
    n_test = n_total - n_train - n_val  # Maradék minden esetben pontosan elosztva

    split_counts = [n_train, n_val, n_test]
    index = 0

    for split, count in zip(splits, split_counts):
        split_cat_folder = os.path.join(output_root, split, category)
        os.makedirs(split_cat_folder, exist_ok=True)

        for img_path in images[index:index + count]:
            dest_path = os.path.join(split_cat_folder, os.path.basename(img_path))
            shutil.copy2(img_path, dest_path)

        index += count

print("✅ Képek szétosztva: train / val / test.")
print(f"Eredmény itt található: {output_root}")
