#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Párhuzamosított EXIF-statisztika szkript – persistent exiftool hívással 50 fájlonként
------------------------------------------------------------------------------
Fő jellemzők:
  - Rekurzív bejárás: Gyökér és almappák
  - Minden batch-ben (pl. 50 képfájl) egyetlen exiftool hívás, ami jelentősen csökkenti a folyamatindítási overhead-et.
  - Preferált EXIF kulcsok használata: pl. "EXIF:ISO", "EXIF:ImageWidth", stb.
  - Hiánykezelés: missing_exif, unreadable, invalid_date
  - Összesített adatok CSV-be írása (exif_summary_parallel.csv)
  
Követelmények:
    pip install PyExifTool tqdm Pillow
    Telepítve kell legyen az exiftool parancssori eszköz (lásd: https://exiftool.org/)
"""

import os
import csv
import json
import warnings
from multiprocessing import Pool, cpu_count
from collections import Counter
from tqdm import tqdm

import exiftool  # PyExifTool

# Elnyomjuk a PIL figyelmeztetéseit
warnings.filterwarnings("ignore", category=UserWarning, module="PIL")

# Preferált exiftool kulcsok az egyes mezőkhöz
preferred_exif_keys = {
    'Make': "EXIF:Make",
    'Model': "EXIF:Model",
    'ExifImageWidth': "EXIF:ImageWidth",      # preferált: EXIF:ImageWidth
    'ExifImageHeight': "EXIF:ImageHeight",    # preferált: EXIF:ImageHeight
    'ISOSpeedRatings': "EXIF:ISO",
    'ExposureTime': "EXIF:ExposureTime",
    'FNumber': "EXIF:FNumber",
    'FocalLength': "EXIF:FocalLength",
    'ExposureProgram': "EXIF:ExposureProgram",
    'MeteringMode': "EXIF:MeteringMode",
    'Flash': "EXIF:Flash",
    'WhiteBalance': "EXIF:WhiteBalance",
    'DateTimeOriginal': "EXIF:DateTimeOriginal",
}

# Megjelenítendő label-ek a CSV-hez
exif_labels = {
    'Make': 'Gyártó',
    'Model': 'Modell',
    'ExifImageWidth': 'Szélesség',
    'ExifImageHeight': 'Magasság',
    'ISOSpeedRatings': 'ISO',
    'ExposureTime': 'Záridő',
    'FNumber': 'Rekesz (blende)',
    'FocalLength': 'Fókusztáv',
    'ExposureProgram': 'Expozíciós mód',
    'MeteringMode': 'Fénymérés',
    'Flash': 'Vaku',
    'WhiteBalance': 'Fehéregyensúly',
    'DateTimeOriginal': 'Készítés ideje'
}

# Elfogadott fájlkiterjesztések
allowed_extensions = {'.jpg', '.jpeg', '.nef'}

def process_batch(file_list):
    """
    Egy adott batch (például 50 képfájl) feldolgozása:
      - Egyetlen exiftool hívással lekéri a metaadatokat az összes file-ra.
      - Az exiftool outputját JSON-ként dekódolja, majd az egyes file-ok metaadatait feldolgozza a preferált kulcsok alapján.
      - Aggregálja a statisztikákat: fájlok száma, összes méret, fájltípus-összesítés, valamint a fontos EXIF mezők gyakorisága.
    Ha az exiftool hívás valamilyen okból hibás, fallbackként per file próbálkozunk a PIL módszerrel.
    """
    # Inicializáljuk a batch eredmény aggregátort
    batch_result = {
        'file_count': 0,
        'total_size': 0,
        'file_type_counts': Counter(),
        'missing_exif': 0,
        'unreadable': 0,
        'invalid_date': 0,
        'exif_fields': { label: Counter() for label in exif_labels.values() }
    }
    try:
        # Egy exiftool hívás az összes fájlra a batch-ben
        with exiftool.ExifTool() as et:
            # Összeállítjuk a paramétereket: először a "-j", majd a file útvonalak (bytes-ban)
            args = [b"-j"] + [f.encode("utf-8") for f in file_list]
            output = et.execute(*args)
        if isinstance(output, bytes):
            output = output.decode("utf-8")
        metadata_list = json.loads(output)
        
        # Feltételezzük, hogy a metadata_list sorrendje megfelel a file_list sorrendjének
        for file_path, meta in zip(file_list, metadata_list):
            result = {}
            # Fájlméret: próbáljuk a meta adatból ("File:FileSize"); ha nincs, akkor os.path.getsize
            file_size = meta.get("File:FileSize")
            if file_size is None:
                try:
                    file_size = os.path.getsize(file_path)
                except Exception:
                    file_size = 0
            result['file_size'] = file_size
            result['extension'] = os.path.splitext(file_path)[1].lower()
            result['exif'] = {}

            # Közvetlenül lekérjük a preferált kulcsokat
            for key, pref_key in preferred_exif_keys.items():
                value = meta.get(pref_key)
                if value is not None:
                    result['exif'][key] = value

            # Fallback: ha a képméret (szélesség/magasság) hiányzik, próbáljuk PIL-lel
            if ('ExifImageWidth' not in result['exif'] or 'ExifImageHeight' not in result['exif']):
                try:
                    from PIL import Image
                    with Image.open(file_path) as img:
                        resolution = img.size
                    result['exif']['ExifImageWidth'] = resolution[0]
                    result['exif']['ExifImageHeight'] = resolution[1]
                except Exception:
                    pass

            # Ha egyetlen fontos adat sincs, jelöljük hiányosnak
            if not result['exif']:
                result['missing_exif'] = 1
            else:
                result['missing_exif'] = 0

            # Aggregálás
            batch_result['file_count'] += 1
            batch_result['total_size'] += result.get('file_size', 0)
            batch_result['file_type_counts'][result.get('extension', '')] += 1
            batch_result['missing_exif'] += result.get('missing_exif', 0)

            # A statisztikákhoz frissítjük az EXIF mezőket is
            for key, label in exif_labels.items():
                if key in result['exif']:
                    value = result['exif'][key]
                    if key == 'DateTimeOriginal':
                        try:
                            year = str(value)[:4]
                            batch_result['exif_fields'][label][year] += 1
                        except Exception:
                            batch_result['invalid_date'] += 1
                    else:
                        batch_result['exif_fields'][label][str(value)] += 1

    except Exception as e:
        # Ha a batch exiftool hívás hibás, akkor fallback: file-enként feldolgozás PIL-módszerrel
        for file_path in file_list:
            result = {}
            try:
                file_size = os.path.getsize(file_path)
            except Exception:
                file_size = 0
            result['file_size'] = file_size
            result['extension'] = os.path.splitext(file_path)[1].lower()
            try:
                from PIL import Image, ExifTags
                with Image.open(file_path) as img:
                    resolution = img.size
                result['exif'] = {
                    'ExifImageWidth': resolution[0],
                    'ExifImageHeight': resolution[1]
                }
                result['missing_exif'] = 1
            except Exception:
                result['unreadable'] = 1
                result['missing_exif'] = 1

            batch_result['file_count'] += 1
            batch_result['total_size'] += result.get('file_size', 0)
            batch_result['file_type_counts'][result.get('extension', '')] += 1
            batch_result['missing_exif'] += result.get('missing_exif', 0)
    return batch_result

def merge_results(result_list):
    """
    Több batch eredményét összevonja egy összesített statisztikává.
    """
    merged = {
        'file_count': 0,
        'total_size': 0,
        'file_type_counts': Counter(),
        'missing_exif': 0,
        'unreadable': 0,
        'invalid_date': 0,
        'exif_fields': { label: Counter() for label in exif_labels.values() }
    }
    for res in result_list:
        merged['file_count'] += res['file_count']
        merged['total_size'] += res['total_size']
        merged['missing_exif'] += res['missing_exif']
        merged['unreadable'] += res['unreadable']
        merged['invalid_date'] += res['invalid_date']
        merged['file_type_counts'].update(res['file_type_counts'])
        for label in exif_labels.values():
            merged['exif_fields'][label].update(res['exif_fields'][label])
    return merged

def chunk_list(lst, chunk_size):
    """
    Darabolja a listát adott méretű csomagokra.
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def scan_directory(root):
    """
    Rekurzív bejárás a gyökér- és almappákban.
    Visszatér:
      - gyökérmappában lévő képfájlok listájával,
      - almappák -> képfájlok dictionary-jével.
    """
    root_files = []
    subfolders = {}
    for dirpath, dirnames, filenames in os.walk(root):
        filenames = sorted(filenames)
        if os.path.abspath(dirpath) == os.path.abspath(root):
            for file in filenames:
                if os.path.splitext(file)[1].lower() in allowed_extensions:
                    root_files.append(os.path.join(dirpath, file))
        else:
            files_in_folder = []
            for file in filenames:
                if os.path.splitext(file)[1].lower() in allowed_extensions:
                    files_in_folder.append(os.path.join(dirpath, file))
            if files_in_folder:
                subfolders[dirpath] = sorted(files_in_folder)
    return root_files, subfolders

def write_csv(summary, filename="exif_summary_parallel.csv"):
    """
    Az összesített statisztikákat CSV fájlba menti.
    """
    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["Kategória", "Alkategória/Érték", "Darab"])
        writer.writerow(["Fájlok száma", "", summary['file_count']])
        writer.writerow(["Összes fájlméret (Byte)", "", summary['total_size']])
        avg_size = summary['total_size'] / summary['file_count'] if summary['file_count'] > 0 else 0
        writer.writerow(["Átlagos fájlméret (Byte)", "", f"{avg_size:.2f}"])
        writer.writerow([])

        writer.writerow(["Fájltípus statisztika", "", ""])
        for ext, count in summary['file_type_counts'].items():
            writer.writerow([ext, "", count])
        writer.writerow([])

        writer.writerow(["EXIF mezők statisztikája", "", ""])
        for label, counter in summary['exif_fields'].items():
            writer.writerow([label, "", ""])
            for value, count in counter.most_common():
                writer.writerow(["", value, count])
            writer.writerow([])
        writer.writerow(["Hibák", "", ""])
        writer.writerow(["Hiányzó EXIF", "", summary['missing_exif']])
        writer.writerow(["Olvashatatlan képek", "", summary['unreadable']])
        writer.writerow(["Érvénytelen dátum", "", summary['invalid_date']])

def main():
    # A szkript könyvtára mint gyökér
    root = os.getcwd()
    print("Könyvtár beolvasása:", root)
    root_files, subfolders = scan_directory(root)
    all_results = []

    num_processes = cpu_count()
    pool = Pool(processes=num_processes)

    # Gyökérfájlok feldolgozása, 50 képenként
    print("Gyökér fájlok feldolgozása...")
    root_batches = list(chunk_list(root_files, 50))
    root_results = []
    for batch_result in tqdm(pool.imap(process_batch, root_batches), total=len(root_batches)):
        root_results.append(batch_result)
    all_results.extend(root_results)

    # Almappák feldolgozása
    for folder, files in sorted(subfolders.items()):
        print(f"Feldolgozás: {folder}")
        folder_batches = list(chunk_list(files, 50))
        folder_results = []
        for batch_result in tqdm(pool.imap(process_batch, folder_batches), total=len(folder_batches)):
            folder_results.append(batch_result)
        all_results.extend(folder_results)

    pool.close()
    pool.join()

    summary = merge_results(all_results)
    write_csv(summary)
    print("CSV mentve:", "exif_summary_parallel.csv")

if __name__ == '__main__':
    main()
