# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "Pillow",
# ]
# ///

"""Validate training dataset structure and content."""

import argparse
import sys
from pathlib import Path
from PIL import Image


def validate_dataset(data_dir: Path, caption_ext: str = "txt"):
    """Validate a training dataset."""
    
    print(f"🔍 Validating dataset: {data_dir}")
    print()
    
    if not data_dir.exists():
        print(f"❌ Error: Directory not found: {data_dir}", file=sys.stderr)
        return False
    
    # Supported image extensions
    image_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    
    # Find all images
    images = []
    for ext in image_exts:
        images.extend(data_dir.glob(f"*{ext}"))
        images.extend(data_dir.glob(f"*{ext.upper()}"))
    
    if not images:
        print(f"❌ Error: No images found in {data_dir}")
        return False
    
    print(f"📁 Found {len(images)} images")
    
    # Check for captions
    images_with_captions = 0
    images_without_captions = []
    caption_lengths = []
    
    # Track resolutions
    resolutions = {}
    corrupted_images = []
    
    for img_path in images:
        # Check for caption
        caption_path = img_path.with_suffix(f".{caption_ext}")
        if caption_path.exists():
            images_with_captions += 1
            caption_text = caption_path.read_text().strip()
            caption_lengths.append(len(caption_text))
        else:
            images_without_captions.append(img_path.name)
        
        # Validate image
        try:
            with Image.open(img_path) as img:
                res = f"{img.width}x{img.height}"
                resolutions[res] = resolutions.get(res, 0) + 1
                
                # Check for transparency
                if img.mode in ("RGBA", "P"):
                    has_alpha = True
                else:
                    has_alpha = False
                    
        except Exception as e:
            corrupted_images.append((img_path.name, str(e)))
    
    # Report findings
    print()
    print(f"📝 Captions:")
    print(f"   With captions: {images_with_captions}/{len(images)}")
    
    if images_with_captions > 0:
        avg_len = sum(caption_lengths) / len(caption_lengths)
        print(f"   Avg caption length: {avg_len:.0f} chars")
    
    if images_without_captions:
        print(f"   ⚠️  Missing captions for {len(images_without_captions)} images:")
        for name in images_without_captions[:5]:
            print(f"      - {name}")
        if len(images_without_captions) > 5:
            print(f"      ... and {len(images_without_captions) - 5} more")
    
    print()
    print(f"🖼️  Resolutions:")
    for res, count in sorted(resolutions.items(), key=lambda x: -x[1]):
        print(f"   {res}: {count} images")
    
    if corrupted_images:
        print()
        print(f"💥 Corrupted images:")
        for name, error in corrupted_images[:5]:
            print(f"   - {name}: {error}")
    
    # Warnings
    print()
    print(f"⚠️  Warnings:")
    
    if len(resolutions) > 3:
        print(f"   - Multiple resolutions detected. Consider standardizing to 512 or 1024.")
    
    if images_with_captions < len(images) * 0.9:
        print(f"   - Less than 90% of images have captions. Training quality may suffer.")
    
    low_res = sum(1 for res, count in resolutions.items() 
                  if int(res.split("x")[0]) < 512)
    if low_res > 0:
        print(f"   - Some images are below 512px. Consider upscaling for better quality.")
    
    # Summary
    print()
    is_valid = (
        images_with_captions > 0 and
        len(corrupted_images) == 0
    )
    
    if is_valid:
        print(f"✅ Dataset is valid and ready for training!")
    else:
        print(f"❌ Dataset has issues. Please fix before training.")
    
    return is_valid


def main():
    parser = argparse.ArgumentParser(
        description="Validate training dataset structure and content"
    )
    parser.add_argument(
        "--data_dir",
        type=Path,
        required=True,
        help="Path to dataset directory",
    )
    parser.add_argument(
        "--caption_ext",
        default="txt",
        help="Caption file extension (default: txt)",
    )
    
    args = parser.parse_args()
    
    is_valid = validate_dataset(args.data_dir, args.caption_ext)
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
