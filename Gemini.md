# Project Overview: python-libphash

`python-libphash` provides high-performance Python bindings for the `libphash` C library. It is designed for perceptual image hashing, which allows for image similarity detection by generating hashes that remain similar even if the image is resized, compressed, or slightly altered.

## System Architecture

The project is structured in three distinct layers to ensure both high performance and Pythonic ease of use:

1.  **Native Layer (`native/libphash`)**: A standalone C library that implements the core hashing algorithms and image processing logic (using `stb_image` for decoding).
2.  **Binding Layer (`src/libphash/_build.py`)**: Uses **CFFI (C Foreign Function Interface)** in out-of-line ABI mode to bridge the C library with Python. This layer defines the C structures and functions exposed to Python.
3.  **Python Layer (`src/libphash/`)**: Provides a high-level, object-oriented API (via `ImageContext`) for developers. It handles memory management (using context managers) and provides convenient properties for accessing various hashes.

## Native Submodule Analysis

The project includes a dependent repository as a git submodule:

*   **Repository**: `https://github.com/gudoshnikovn/libphash.git`
*   **Path**: `native/libphash`
*   **Status**: Currently tracking version `1.6.1`.
*   **Role**: It serves as the "engine" of the project. It contains the C source code for all supported hashing algorithms.

### Submodule Structure:
- `include/libphash.h`: The public API header defining the interface for FFI.
- `src/`: The core implementation logic.
    - `core.c`: Context management and lifecycle.
    - `image.c`: Grayscale conversion and bilinear interpolation.
    - `hashes/`: Individual algorithm implementations (pHash, dHash, aHash, etc.).
- `vendor/`: Bundled dependencies like `stb_image.h` to ensure zero external binary dependencies.

## Key Components & Workflow

### 1. Image Processing Pipeline
When an image is loaded via `ImageContext`, the following happens in the native layer:
- The image is decoded into raw RGB/RGBA pixels.
- It is converted to grayscale using configurable weights.
- It is resized to the dimensions required by the specific hashing algorithm using bilinear interpolation for high fidelity.

### 2. Supported Algorithms
- **64-bit Integer Hashes**: `ahash`, `dhash`, `phash`, `whash`, `mhash`.
- **Complex Digests**: `bmh` (Block Mean), `color_hash`, `radial_hash` (Rotation invariant).

### 3. Memory Management
The Python `ImageContext` class automatically calls `ph_free()` in the C layer when the context is closed or the object is garbage collected, preventing memory leaks of large image buffers.

## File Structure Breakdown

```text
.
├── native/libphash/      # [SUBMODULE] Core C implementation
│   ├── include/          # Public C headers
│   └── src/              # C source code (Core & Algorithms)
├── src/libphash/         # Python package source
│   ├── _build.py         # CFFI build script (C-Python bridge)
│   ├── context.py        # High-level ImageContext API
│   ├── ph_types.py       # Python representations of C types (Digest, etc.)
├── tests/                # Comprehensive pytest suite
├── pyproject.toml        # Build system configuration
└── README.md             # Standard usage documentation
```

## Development Environment

The project is managed using **uv**. It is recommended to use `uv` for all development tasks (installing dependencies, running tests, building).

### Commands:
- **Build/Install**: `uv pip install -e .`
- **Run Tests**: `uv run --with pytest pytest`
- **Lint/Check**: `uv run ruff check .`
