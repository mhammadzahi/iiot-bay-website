import os, sys, random
from pathlib import Path
from PIL import Image
import piexif
from datetime import datetime


SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".webp"]


def load_keywords(keywords_file):
    with open(keywords_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Support both comma-separated and newline-separated
    keywords = [
        kw.strip()
        for kw in content.replace(",", "\n").split("\n")
        if kw.strip()
    ]
    return keywords


def build_metadata_strings(keywords, filename):
    keyword_string = ", ".join(keywords)
    title = f"{filename} - {keywords[0] if keywords else ''}"
    description = f"Image related to: {keyword_string}"
    return title, description, keyword_string


def inject_jpeg_metadata(img_path, keywords):
    filename = img_path.stem
    title, description, keyword_string = build_metadata_strings(keywords, filename)

    img = Image.open(img_path)

    try:
        exif_dict = piexif.load(img.info.get("exif", b""))
    except Exception:
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

    # Inject metadata
    exif_dict["0th"][piexif.ImageIFD.ImageDescription] = description.encode("utf-8")
    exif_dict["0th"][piexif.ImageIFD.XPTitle] = title.encode("utf-16le")
    exif_dict["0th"][piexif.ImageIFD.XPKeywords] = keyword_string.encode("utf-16le")
    exif_dict["0th"][piexif.ImageIFD.XPComment] = description.encode("utf-16le")

    # Add current datetime
    now = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
    exif_dict["0th"][piexif.ImageIFD.DateTime] = now.encode("utf-8")

    exif_bytes = piexif.dump(exif_dict)
    img.save(img_path, exif=exif_bytes)


def inject_png_metadata(img_path, keywords):
    filename = img_path.stem
    title, description, keyword_string = build_metadata_strings(keywords, filename)

    img = Image.open(img_path)
    metadata = img.info

    metadata["Title"] = title
    metadata["Description"] = description
    metadata["Keywords"] = keyword_string

    img.save(img_path, pnginfo=None)


def inject_webp_metadata(img_path, keywords):
    filename = img_path.stem
    title, description, keyword_string = build_metadata_strings(keywords, filename)

    img = Image.open(img_path)

    img.save(
        img_path,
        format="WEBP",
        quality=100,
        method=6,
    )


def process_images(folder_path, keywords):
    folder = Path(folder_path)

    if not folder.exists():
        print("Folder does not exist.")
        return

    for img_path in folder.rglob("*"):
        if img_path.suffix.lower() not in SUPPORTED_FORMATS:
            continue

        print(f"Processing: {img_path.name}")
        
        # Select 5 random keywords for this image
        random_keywords = random.sample(keywords, min(5, len(keywords)))

        if img_path.suffix.lower() in [".jpg", ".jpeg"]:
            inject_jpeg_metadata(img_path, random_keywords)
        elif img_path.suffix.lower() == ".png":
            inject_png_metadata(img_path, random_keywords)
        elif img_path.suffix.lower() == ".webp":
            inject_webp_metadata(img_path, random_keywords)

    print("Done.")


def main():
    folder_path = "static/img"
    keywords_file = "keywords.txt"

    keywords = load_keywords(keywords_file)
    random.shuffle(keywords)
    process_images(folder_path, keywords)


if __name__ == "__main__":
    main()
