# Project Map: python-libphash (v1.3.0)

This file serves as a high-level entry point for navigating the `python-libphash` project. 

## Versioning & Core
- **Python Package Version**: `1.4.1`
- **Core C Engine (`libphash`)**: `1.10.4` (tracked via `native/libphash` submodule)
  - **Supported Hashes**:
    - **64-bit Integer Hashes**: `ahash`, `dhash`, `phash`, `whash`, `mhash`, `color_hash`.
    - **Complex Digests**: `bmh`, `color_moments_hash`, `radial_hash`.
- **Primary Goal**: High-performance perceptual hashing with zero-copy I/O and SIMD-accelerated decoding.

## Documentation Index
| Topic | Location | Description |
|:---|:---|:---|
| **Quick Start** | [README.md](file:///Users/gudoshnikov_na/Programming/Python/python-libphash/README.md) | Installation, basic usage, and API overview. |
| **System Architecture** | [architecture.md](file:///Users/gudoshnikov_na/Programming/C/libphash/docs/architecture.md) | C-engine design, mmap-based I/O, and component breakdown. |
| **Algorithm Details** | [algorithms.md](file:///Users/gudoshnikov_na/Programming/C/libphash/docs/algorithms.md) | Mathematical foundations of pHash, dHash, aHash, etc. |
| **Development Guide** | [development.md](file:///Users/gudoshnikov_na/Programming/C/libphash/docs/development.md) | Build instructions, coding standards, and testing procedures. |
| **Build System** | [pyproject.toml](file:///Users/gudoshnikov_na/Programming/Python/python-libphash/pyproject.toml) | `cibuildwheel` config and build-time dependencies. |

## Project Structure
- `native/libphash/`: Core C library (The "Engine").
- `src/libphash/`: Python CFFI bindings and high-level `ImageContext` API.
- `benchmarks/`: Production-ready benchmark suite.
  - `utils.py`: Shared augmentation and data management logic.
  - `generate_data.py`: CLI tool for generating test datasets (JPEG/PNG).
  - `run_speed.py`: Performance throughput comparison.
  - `run_quality.py`: Accuracy metrics (PR-AUC/F1) using augmented datasets.
  - `data/jpeg/`: Consistently structured JPEG test data.
  - `data/png/`: Consistently structured PNG test data.
- `tests/`: API verification and stability tests.

## Key Performance Features
- **Zero-Copy**: mmap-based loading directly into TurboJPEG/libpng.
- **SIMD**: ARM NEON and x86 SSE/AVX2 acceleration for decoding and hashing.
- **Fast DCT**: Optimized integer iDCT for pHash.

---
*Last Updated: 2026-02-23*
