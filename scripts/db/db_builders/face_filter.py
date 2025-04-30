import os
import cv2
import shutil
from tqdm import tqdm

def move_images_with_faces(folder_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces_dir = os.path.join(folder_path, "faces")
    os.makedirs(faces_dir, exist_ok=True)

    image_files = [f for f in os.listdir(folder_path)
                   if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    print(f"🔎 Vizsgált képek száma: {len(image_files)}")

    moved_count = 0

    for filename in tqdm(image_files, desc="📷 Arcok keresése"):
        file_path = os.path.join(folder_path, filename)
        try:
            img = cv2.imread(file_path)
            if img is None:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            if len(faces) > 0:
                shutil.move(file_path, os.path.join(faces_dir, filename))
                moved_count += 1
        except Exception as e:
            print(f"⚠️ Hiba a képnél: {filename} – {e}")

    print(f"✅ Áthelyezett képek száma: {moved_count}")

# 🔁 Automatikusan abban a mappában fut, ahol a szkript van
if __name__ == "__main__":
    current_folder = os.path.dirname(os.path.abspath(__file__))
    print(f"📂 Futtatás helye: {current_folder}")
    move_images_with_faces(current_folder)
