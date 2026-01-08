from pathlib import Path
import pytest


def get_test_images_dir() -> Path:
    """Locate the directory containing test images relative to this file."""
    return Path(__file__).resolve().parent.parent / "native" / "libphash" / "tests"


@pytest.fixture
def image_path() -> str:
    """Return the path to the primary test image."""
    path = get_test_images_dir() / "photo.jpeg"
    if not path.exists():
        pytest.skip(f"Test image not found at {path}")
    return str(path)


@pytest.fixture
def sample_jpeg_bytes(image_path: str) -> bytes:
    """Read the primary test image into memory as bytes."""
    with open(image_path, "rb") as f:
        return f.read()
