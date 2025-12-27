import shutil
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "phai-lab_files"
BACKUP_DIR = ASSETS / "originals"
TARGET_SIZE = 512


def _largest_face(faces):
    # faces: [(x,y,w,h), ...]
    return max(faces, key=lambda f: f[2] * f[3])


def crop_to_face_square(img_bgr):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    h, w = img_bgr.shape[:2]

    if len(faces) == 0:
        # Fallback: centered square crop
        side = min(h, w)
        cx, cy = w // 2, h // 2
        x1 = max(0, cx - side // 2)
        y1 = max(0, cy - side // 2)
        x2 = x1 + side
        y2 = y1 + side
        return img_bgr[y1:y2, x1:x2]

    x, y, fw, fh = _largest_face(faces)
    fx = x + fw / 2.0
    fy = y + fh / 2.0

    # square side with padding around face
    side = int(max(fw, fh) * 2.2)
    side = max(side, 200)
    side = min(side, max(h, w))

    x1 = int(round(fx - side / 2))
    y1 = int(round(fy - side / 2))
    x2 = x1 + side
    y2 = y1 + side

    # clamp into image
    if x1 < 0:
        x2 -= x1
        x1 = 0
    if y1 < 0:
        y2 -= y1
        y1 = 0
    if x2 > w:
        shift = x2 - w
        x1 -= shift
        x2 = w
        x1 = max(0, x1)
    if y2 > h:
        shift = y2 - h
        y1 -= shift
        y2 = h
        y1 = max(0, y1)

    # ensure square within bounds
    x2 = min(w, x2)
    y2 = min(h, y2)
    crop = img_bgr[y1:y2, x1:x2]

    # If the crop isn't square due to bounds, center-crop to square
    ch, cw = crop.shape[:2]
    side2 = min(ch, cw)
    cx2, cy2 = cw // 2, ch // 2
    x1b = max(0, cx2 - side2 // 2)
    y1b = max(0, cy2 - side2 // 2)
    crop = crop[y1b:y1b + side2, x1b:x1b + side2]

    return crop


def process_one(path: Path) -> None:
    img = cv2.imread(str(path))
    if img is None:
        raise RuntimeError(f"Failed to read image: {path}")

    cropped = crop_to_face_square(img)
    resized = cv2.resize(cropped, (TARGET_SIZE, TARGET_SIZE), interpolation=cv2.INTER_AREA)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / path.name
    if not backup_path.exists():
        shutil.copy2(path, backup_path)

    # Overwrite as JPEG with good quality
    ok = cv2.imwrite(str(path), resized, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    if not ok:
        raise RuntimeError(f"Failed to write image: {path}")


def main() -> None:
    targets = [
        ASSETS / "zhiwenfan.jpg",
        ASSETS / "nuochen.jpg",
    ]

    for p in targets:
        if not p.exists():
            raise FileNotFoundError(p)
        process_one(p)
        print(f"Processed {p.relative_to(ROOT)} -> {TARGET_SIZE}x{TARGET_SIZE}")


if __name__ == "__main__":
    main()




