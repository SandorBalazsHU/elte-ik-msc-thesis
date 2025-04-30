#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teszt szkript az EXIFTool metaadatok kiolvasásához.
Futtatás:
    python exiftool_test.py <fájlelérési út>
Például:
    python exiftool_test.py my_image.nef

A szkript kinyomtatja a megadott kép összes metaadatát JSON formátumban,
amit könnyen átnézhetsz és megoszthatsz, hogy finomítsuk a fő szkriptet.
"""

import argparse
import json
import exiftool

def main():
    parser = argparse.ArgumentParser(
        description="Teszt szkript az EXIFTool metaadatok megjelenítéséhez."
    )
    parser.add_argument("file", help="A kép fájl elérési útvonala (.nef, .jpg, .jpeg stb.)")
    args = parser.parse_args()

    with exiftool.ExifTool() as et:
        # A '-j' kapcsoló JSON kimenetet eredményez
        output = et.execute(b"-j", args.file.encode("utf-8"))
        # Ha az output bytes, dekódoljuk, ha nem, akkor hagyjuk változatlanul.
        if isinstance(output, bytes):
            output = output.decode("utf-8")
        try:
            metadata_list = json.loads(output)
        except Exception as e:
            print("Hiba a JSON parse során:", e)
            return

    if metadata_list:
        # Szép formázott JSON kimenet
        print(json.dumps(metadata_list[0], indent=4, ensure_ascii=False))
    else:
        print("A fájlhoz nem található metaadat.")

if __name__ == "__main__":
    main()
