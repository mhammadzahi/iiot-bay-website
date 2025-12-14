#!/usr/bin/env python3
"""
Image to WebP Converter
Converts PNG, JPEG, JPG images to WebP format
"""

import os
from pathlib import Path
from PIL import Image


def convert_to_webp(source_path, quality=85, keep_original=True):
    """
    Convert an image to WebP format
    
    Args:
        source_path: Path to the source image
        quality: WebP quality (0-100, default 85)
        keep_original: Keep the original file (default True)
    
    Returns:
        Path to the converted WebP file or None if failed
    """
    try:
        # Open the image
        img = Image.open(source_path)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        # Generate WebP filename
        webp_path = source_path.rsplit('.', 1)[0] + '.webp'
        
        # Save as WebP
        img.save(webp_path, 'WEBP', quality=quality, method=6)
        
        # Get file sizes
        original_size = os.path.getsize(source_path)
        webp_size = os.path.getsize(webp_path)
        savings = ((original_size - webp_size) / original_size) * 100
        
        print(f"✓ Converted: {os.path.basename(source_path)}")
        print(f"  Original: {original_size / 1024:.2f} KB → WebP: {webp_size / 1024:.2f} KB")
        print(f"  Saved: {savings:.1f}%\n")
        
        # Remove original if requested
        if not keep_original:
            os.remove(source_path)
            print(f"  Removed original: {os.path.basename(source_path)}\n")
        
        return webp_path
        
    except Exception as e:
        print(f"✗ Error converting {source_path}: {e}\n")
        return None


def convert_directory(directory, quality=85, keep_original=True, recursive=True):
    """
    Convert all images in a directory to WebP
    
    Args:
        directory: Directory path to scan
        quality: WebP quality (0-100)
        keep_original: Keep original files
        recursive: Scan subdirectories
    """
    # Supported image formats
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')
    
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"Error: Directory '{directory}' does not exist!")
        return
    
    # Find all image files
    if recursive:
        image_files = [
            f for f in directory_path.rglob('*')
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
    else:
        image_files = [
            f for f in directory_path.glob('*')
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
    
    if not image_files:
        print(f"No images found in '{directory}'")
        return
    
    print(f"\nFound {len(image_files)} image(s) to convert\n")
    print("=" * 60)
    
    converted_count = 0
    failed_count = 0
    
    for img_file in image_files:
        result = convert_to_webp(str(img_file), quality=quality, keep_original=keep_original)
        if result:
            converted_count += 1
        else:
            failed_count += 1
    
    print("=" * 60)
    print(f"\nConversion complete!")
    print(f"✓ Successfully converted: {converted_count}")
    if failed_count > 0:
        print(f"✗ Failed: {failed_count}")
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert images to WebP format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all images in static/img (keep originals)
  python convert_to_webp.py static/img
  
  # Convert with custom quality and remove originals
  python convert_to_webp.py static/img -q 90 --no-keep
  
  # Convert single file
  python convert_to_webp.py static/img/logo.png
  
  # Non-recursive (current directory only)
  python convert_to_webp.py static/img --no-recursive
        """
    )
    
    parser.add_argument(
        'path',
        help='Path to image file or directory'
    )
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        help='WebP quality (0-100, default: 85)'
    )
    parser.add_argument(
        '--no-keep',
        action='store_true',
        help='Remove original files after conversion'
    )
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not scan subdirectories'
    )
    
    args = parser.parse_args()
    
    # Validate quality
    if not 0 <= args.quality <= 100:
        print("Error: Quality must be between 0 and 100")
        return
    
    path = Path(args.path)
    
    # Check if path exists
    if not path.exists():
        print(f"Error: Path '{args.path}' does not exist!")
        return
    
    print("\n" + "=" * 60)
    print("WebP Image Converter")
    print("=" * 60)
    
    # Single file or directory
    if path.is_file():
        if path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif'):
            convert_to_webp(str(path), quality=args.quality, keep_original=not args.no_keep)
        else:
            print(f"Error: Unsupported file format: {path.suffix}")
    else:
        convert_directory(
            args.path,
            quality=args.quality,
            keep_original=not args.no_keep,
            recursive=not args.no_recursive
        )


if __name__ == '__main__':
    main()
