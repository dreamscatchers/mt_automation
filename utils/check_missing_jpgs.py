import os
import re
from PIL import Image

SRC_DIR = os.path.expanduser(
    "~/projects/master_touch_meditation/sequence/sources"
)
JPG_DIR = os.path.expanduser(
    "~/projects/master_touch_meditation/sequence"
)

pattern = re.compile(r"^(\d+)\.png$", re.IGNORECASE)

print(f"Checking PNG files in: {SRC_DIR}")
print(f"Against/into JPG files in:  {JPG_DIR}\n")

missing = []

for filename in os.listdir(SRC_DIR):
    match = pattern.match(filename)
    if not match:
        continue  # пропускаем всё, что не <number>.png

    number = match.group(1)
    png_name = filename
    png_path = os.path.join(SRC_DIR, png_name)
    jpg_name = f"{number}.jpg"
    jpg_path = os.path.join(JPG_DIR, jpg_name)

    if not os.path.isfile(jpg_path):
        print(f"MISSING JPG: {jpg_name}  -> creating from {png_name}")
        missing.append(jpg_name)

        # Открываем PNG и конвертируем в JPG того же размера
        img = Image.open(png_path)

        # Обрабатываем прозрачность, если есть
        if img.mode in ("RGBA", "LA"):
            # Композиция на чёрный фон (можно заменить на белый (255,255,255))
            background = Image.new("RGB", img.size, (0, 0, 0))
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert("RGB")

        # Сохраняем JPG
        img.save(jpg_path, "JPEG", quality=95)
        print(f"CREATED JPG: {jpg_path}")
    else:
        # Для контроля можно раскомментировать:
        # print(f"OK: {jpg_name} exists")
        pass

if not missing:
    print("\nAll JPG files were already present.")
else:
    print("\nNewly created JPG files:")
    for f in missing:
        print(" -", f)
