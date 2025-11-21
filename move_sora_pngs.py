import os
import re
import shutil

SOURCE_DIR = os.path.expanduser(
    "~/projects/master_touch_meditation/sequence/sources"
)
TARGET_DIR = os.path.join(SOURCE_DIR, "sora")

# Создаём папку sora, если её нет
os.makedirs(TARGET_DIR, exist_ok=True)

# Ищем ИМЕННО <число>_.png, например: 1_.png, 25_.png, 276_.png
pattern = re.compile(r"^\d+_\.png$", re.IGNORECASE)

print(f"Source: {SOURCE_DIR}")
print(f"Target: {TARGET_DIR}")
print("Scanning...\n")

for filename in os.listdir(SOURCE_DIR):
    src = os.path.join(SOURCE_DIR, filename)

    # Пропускаем поддиректории
    if not os.path.isfile(src):
        print(f"SKIP (not a file): {filename}")
        continue

    if not filename.lower().endswith(".png"):
        print(f"SKIP (not png):    {filename}")
        continue

    if pattern.match(filename):
        dst = os.path.join(TARGET_DIR, filename)
        print(f"MOVE:              {filename}  ->  sora/")
        shutil.move(src, dst)
    else:
        print(f"SKIP (name fail):  {filename} (not <Number>_.png)")

print("\nDone.")
