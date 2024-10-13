import os
import random
import shutil

def split_dataset(input_folder, output_folder, train_ratio=0.5, val_ratio=0.25):
    # Ellenőrizzük az input mappa létezését
    if not os.path.exists(input_folder):
        print(f"Az input mappa '{input_folder}' nem létezik.")
        return
    
    # Készítjük az output mappákat
    train_folder = os.path.join(output_folder, 'train')
    val_folder = os.path.join(output_folder, 'val')
    test_folder = os.path.join(output_folder, 'test')

    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    # Kinyerjük az összes JPG fájlt az input mappából
    jpg_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.jpg')]

    # Vegyes sorrendbe rendezzük a fájlokat
    random.shuffle(jpg_files)

    # Kiszámítjuk a darabszámokat a három mappa között
    total_files = len(jpg_files)
    train_count = int(total_files * train_ratio)
    val_count = int(total_files * val_ratio)

    # Kimásoljuk a fájlokat a megfelelő mappákba
    train_files = jpg_files[:train_count]
    val_files = jpg_files[train_count:train_count + val_count]
    test_files = jpg_files[train_count + val_count:]

    for filename in train_files:
        shutil.copy(os.path.join(input_folder, filename), os.path.join(train_folder, filename))

    for filename in val_files:
        shutil.copy(os.path.join(input_folder, filename), os.path.join(val_folder, filename))

    for filename in test_files:
        shutil.copy(os.path.join(input_folder, filename), os.path.join(test_folder, filename))

    print(f"A fájlok sikeresen áthelyezve a '{output_folder}' mappába.")

# Példa használat
input_folder = './'
output_folder = './'
split_dataset(input_folder, output_folder, train_ratio=0.5, val_ratio=0.25)
