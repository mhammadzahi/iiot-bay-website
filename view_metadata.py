import sys
from pathlib import Path
from PIL import Image
import piexif

SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".webp"]


def show_exif(exif_dict):
    # iterate through 0th IFD for our injected tags
    ifd = exif_dict.get("0th", {})
    for tag, value in ifd.items():
        name = piexif.TAGS["0th"].get(tag, {}).get("name", tag)
        # decode bytes if necessary
        if isinstance(value, bytes):
            try:
                # some values are utf-16le
                value = value.decode("utf-8")
            except Exception:
                try:
                    value = value.decode("utf-16le")
                except Exception:
                    pass
        print(f"  {name}: {value}")


def inspect_image(img_path: Path):
    print(f"\nInspecting '{img_path}'")
    img = Image.open(img_path)
    suffix = img_path.suffix.lower()
    if suffix in [".jpg", ".jpeg"]:
        try:
            exif_dict = piexif.load(img.info.get("exif", b""))
            show_exif(exif_dict)
        except Exception as e:
            print("  (no exif or failed to read)", e)
    elif suffix == ".png":
        info = img.info
        for k, v in info.items():
            print(f"  {k}: {v}")
    elif suffix == ".webp":
        # PIL does not expose metadata much for webp
        print("  (WEBP metadata not supported)")
    else:
        print("  unsupported format")


def main():
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = Path("static/img")

    if path.is_dir():
        for img in path.rglob("*"):
            if img.suffix.lower() in SUPPORTED_FORMATS:
                inspect_image(img)
    elif path.is_file():
        inspect_image(path)
    else:
        print(f"Path {path} does not exist")


if __name__ == "__main__":
    main()
