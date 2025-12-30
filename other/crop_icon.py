#!/usr/bin/env python3
"""
Script to crop an image to 48x48 pixels.
Usage: python crop_icon.py
"""

from PIL import Image
import os

def crop_image_to_48x48(input_path, output_path=None):
    """
    Crop/resize an image to 48x48 pixels.
    
    Args:
        input_path: Path to the input image
        output_path: Path to save the output image (optional)
    """
    # Open the image
    img = Image.open(input_path)
    
    print(f"Original image size: {img.size}")
    
    # Get the smaller dimension to create a square crop
    width, height = img.size
    
    # Calculate crop box to center the crop
    if width > height:
        # Landscape - crop width
        left = (width - height) / 2
        top = 0
        right = left + height
        bottom = height
    else:
        # Portrait or square - crop height if needed
        left = 0
        top = (height - width) / 2
        right = width
        bottom = top + width
    
    # Crop to square first
    img_cropped = img.crop((left, top, right, bottom))
    
    # Resize to 48x48
    img_resized = img_cropped.resize((48, 48), Image.Resampling.LANCZOS)
    
    # Determine output path
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_48x48{ext}"
    
    # Save the image
    img_resized.save(output_path)
    print(f"Cropped image saved to: {output_path}")
    print(f"New image size: {img_resized.size}")
    
    return output_path


if __name__ == "__main__":
    # Path to the input image
    input_image = "static/img/iio-bay-icon.png"
    
    # Check if file exists
    if not os.path.exists(input_image):
        print(f"Error: Image file not found: {input_image}")
        exit(1)
    
    # Crop the image
    output_image = crop_image_to_48x48(input_image)
    print(f"\nSuccess! Image cropped to 48x48 pixels.")
