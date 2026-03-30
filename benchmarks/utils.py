import os
import glob
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
from libphash import ImageContext


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def get_base_files(data_dir, extension="jpg"):
    return sorted(glob.glob(os.path.join(data_dir, f"*.{extension}")))


def generate_augmentations(base_path, output_dir, fmt="JPEG"):
    """
    Generate deterministic augmentations for a single base image.
    Returns list of (path, base_name)
    """
    img = Image.open(base_path).convert("RGB")
    base_name = Path(base_path).stem
    results = []

    ext = "jpg" if fmt == "JPEG" else "png"

    # 0. Base as target format
    p0 = os.path.join(output_dir, f"{base_name}_base.{ext}")
    img.save(p0, fmt)
    results.append((p0, base_name))

    # 1. Resize/Compression
    p1 = os.path.join(output_dir, f"{base_name}_aug_comp.{ext}")
    img_res = img.resize((img.width // 2, img.height // 2))
    if fmt == "JPEG":
        img_res.save(p1, "JPEG", quality=30)
    else:
        img_res.save(p1, "PNG")
    results.append((p1, base_name))

    # 2. Color Shift
    p2 = os.path.join(output_dir, f"{base_name}_aug_color.{ext}")
    img_b = ImageEnhance.Brightness(img).enhance(1.5)
    img_c = ImageEnhance.Contrast(img_b).enhance(0.8)
    img_c.save(p2, fmt)
    results.append((p2, base_name))

    # 3. Blur + Crop
    p3 = os.path.join(output_dir, f"{base_name}_aug_blur.{ext}")
    img_blur = img.filter(ImageFilter.GaussianBlur(1.5))
    w, h = img_blur.size
    img_crop = img_blur.crop(
        (int(w * 0.05), int(h * 0.05), int(w * 0.95), int(h * 0.95))
    )
    img_crop.save(p3, fmt)
    results.append((p3, base_name))

    return results


def get_hash_lp(path, algo_name, ctx=None, mode=None):
    """Get hash from libphash context."""
    if ctx is None:
        with ImageContext(path, load_grayscale=True) as local_ctx:
            if mode and algo_name == "whash":
                local_ctx.set_whash_mode(mode)
            return getattr(local_ctx, algo_name)
    if mode and algo_name == "whash":
        ctx.set_whash_mode(mode)
    return getattr(ctx, algo_name)


def get_hash_ih(path, ih_func):
    """Get hash from imagehash (Pillow)."""
    img = Image.open(path).convert("RGB")
    return ih_func(img)
