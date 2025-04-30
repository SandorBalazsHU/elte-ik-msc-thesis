# elte-ik-msc-thesis
Sándor Balázs diplomamunkája az ELTE IK Programtervező Informatikus mesterszakára, Információs rendszerek szakirányra.


# 📷 SBPhotoThemes180k - Fotóosztályozás neurális hálózatokkal

Ez a projekt egy mesterszakos diplomamunka eredménye, melynek célja egy saját, nagyméretű fotóadatbázis felhasználásával különböző neurális hálózati modellek osztályozási képességeinek vizsgálata.

A projekt része több ezer saját készítésű fénykép feldolgozása, címkézése, valamint a képek alapján történő tanítás és kiértékelés több különböző deep learning modell segítségével.

---

## 🎯 Projekt célja

A cél egy valós, hosszú idő alatt gyűjtött és természetes módon kialakult képadatbázis osztályozása konvolúciós neurális hálózatokkal (CNN), a modellek teljesítményének összehasonlítása, valamint egy kis erőforrásigényű saját modell fejlesztése lokális felhasználásra.

---

## 🗂️ Könyvtárstruktúra

```bash
.
├── literature/           # Összegyűjtött tudományos és technikai irodalom
├── notebooks/            # Jupyter notebook-ok (Google Colab)
│   ├── db/               # Adatbázis építéssel kapcsolatos notebookok
│   ├── phase1/           # Előtanított modellek kiértékelése (0. fázis)
│   ├── phase2/           # Teljes tanítóhalmazos tanítás (1. fázis)
│   ├── phase3/           # Iteratív mintabővítés vizsgálat (2. fázis)
│   └── summary/          # Összegző és összehasonlító notebookok
├── scripts/
│   ├── cnn/              # Modellek tanításához, kiértékeléséhez írt python szkriptek
│   └── db/               # Adatbázis előkészítés és konvertálás (EXIF, címkézés, átméretezés)
├── thesis-latex/         # A diplomamunka LaTeX forrása és ábrái
└── README.md             # Ez a fájl
