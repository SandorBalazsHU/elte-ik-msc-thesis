#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Párhuzamosított EXIF-statisztika szkript – preferált kulcsok használatával
-------------------------------------------------------------------------
Fő jellemzők:
  - Rekurzív bejárás: Gyökér és almappák
  - Az EXIF adatokból csak a valóban releváns, preferált kulcsokat használjuk
    (pl. "EXIF:ISO", "EXIF:ImageWidth" stb.)
  - Hiánykezelés: missing_exif, unreadable, invalid_date
  - Párhuzamos feldolgozás: multiprocessing.Pool, 50 képenként
  - Progress bar: tqdm modul
  - CSV összesítés: exif_summary_parallel.csv

Követelmények:
    pip install PyExifTool tqdm Pillow
    Telepítve legyen az exiftool parancssori eszköz (lásd: https://exiftool.org/)
"""

import os
import csv
import json
import warnings
from multiprocessing import Pool, cpu_count
from collections import Counter
from tqdm import tqdm

import exiftool  # PyExifTool

# FIGYELMEZTETÉS: Elnyomjuk a PIL által generált figyelmeztetéseket
warnings.filterwarnings("ignore", category=UserWarning, module="PIL")

# A statisztikába való gyűjtendő mezők – megjelenítendő label mellett a preferált kulcsokat is megadjuk.
preferred_exif_keys = {
    'Make': "EXIF:Make",
    'Model': "EXIF:Model",
    'ExifImageWidth': "EXIF:ImageWidth",      # használjuk az "EXIF:ImageWidth"-et
    'ExifImageHeight': "EXIF:ImageHeight",    # használjuk az "EXIF:ImageHeight"-et
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

# Megjelenítendő label-ek (CSV-ben) a fenti kulcsokhoz
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

allowed_extensions = {'.jpg', '.jpeg', '.nef'}

def process_file(file_path):
    """
    Egy képfájl feldolgozása:
      - Az exiftool segítségével lekéri a metaadatokat JSON formátumban.
      - A preferált kulcsok alapján feltölt egy dict-et a fontos mezőkkel.
      - Ha például a képméret hiányzik, akkor fallbackként a PIL-t hívja meg.
      - Egyéb hibák esetén jelzi, hogy hiányos az EXIF.
    Visszatér egy dict-tel, amely tartalmazza a fájl méretét, kiterjesztését,
    hibaszámlálókat és a kinyert EXIF adatokat a preferált kulcsok alapján.
    """
    file_stats = {}
    try:
        file_stats['file_size'] = os.path.getsize(file_path)
    except Exception:
        file_stats['file_size'] = 0
    ext = os.path.splitext(file_path)[1].lower()
    file_stats['extension'] = ext

    file_stats['missing_exif'] = 0
    file_stats['unreadable'] = 0
    file_stats['invalid_date'] = 0
    file_stats['exif'] = {}

    try:
        with exiftool.ExifTool() as et:
            output = et.execute(b"-j", file_path.encode("utf-8"))
        if isinstance(output, bytes):
            output = output.decode("utf-8")
        metadata_list = json.loads(output)
        metadata = metadata_list[0] if metadata_list else {}

        # Közvetlenül lekérjük a preferált kulcsokat:
        for key, preferred_key in preferred_exif_keys.items():
            value = metadata.get(preferred_key)
            if value is not None:
                file_stats['exif'][key] = value

        # Képméret fallback: ha az "EXIF:ImageWidth"/"ImageHeight" nem található,
        # próbáljuk meg a PIL-t használni.
        if 'ExifImageWidth' not in file_stats['exif'] or 'ExifImageHeight' not in file_stats['exif']:
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    resolution = img.size
                file_stats['exif']['ExifImageWidth'] = resolution[0]
                file_stats['exif']['ExifImageHeight'] = resolution[1]
            except Exception:
                file_stats['missing_exif'] = 1

        # Ha egyik fontos adat sincs, jelöljük, hogy a képről hiányos az EXIF
        if not file_stats['exif']:
            file_stats['missing_exif'] = 1

    except Exception as e:
        # Ha valami hiba lép fel exiftool használatakor, fallback: próbálkozunk a PIL-el legalább a képmérettel.
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                resolution = img.size
            file_stats['exif']['ExifImageWidth'] = resolution[0]
            file_stats['exif']['ExifImageHeight'] = resolution[1]
            file_stats['missing_exif'] = 1
        except Exception:
            file_stats['unreadable'] = 1
            file_stats['missing_exif'] = 1

    return file_stats

def process_batch(file_list):
    """
    50 képes csomag feldolgozása, a visszaadott eredményeket aggregálja.
    """
    batch_result = {
        'file_count': 0,
        'total_size': 0,
        'file_type_counts': Counter(),
        'missing_exif': 0,
        'unreadable': 0,
        'invalid_date': 0,
        'exif_fields': { label: Counter() for label in exif_labels.values() }
    }
    for file_path in file_list:
        result = process_file(file_path)
        batch_result['file_count'] += 1
        batch_result['total_size'] += result.get('file_size', 0)
        batch_result['file_type_counts'][result.get('extension', '')] += 1
        batch_result['missing_exif'] += result.get('missing_exif', 0)
        batch_result['unreadable'] += result.get('unreadable', 0)
        batch_result['invalid_date'] += result.get('invalid_date', 0)

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
    return batch_result

def merge_results(result_list):
    """
    Egyszerű összesítő függvény több batch eredményeinek egyesítésére.
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
    Kis csomagokra bontás.
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def scan_directory(root):
    """
    Rekurzív bejárása a gyökér- és almappáknak. Visszaadja:
      - Gyökérmappában lévő képfájlok listáját.
      - Almappák -> képfájlok dictionary-jét.
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
    Az összesített statisztikákat CSV fájlba írja.
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
    root = os.getcwd()  # A szkript könyvtára a gyökér
    print("Könyvtár beolvasása:", root)
    root_files, subfolders = scan_directory(root)
    all_results = []

    num_processes = cpu_count()
    pool = Pool(processes=num_processes)

    # Gyökérfájlok feldolgozása (50 képenként)
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
