# libphash API Changes (v1.6.0)

This document provides a technical summary of the new configuration API introduced in libphash v1.6.0. These functions allow fine-tuning the hashing algorithms via the `ph_context_t` object.

## New Configuration Functions

All configuration functions target the opaque `ph_context_t` and are thread-safe (when used on different contexts).

### 1. Brightness Normalization (Gamma)
```c
PH_API void ph_context_set_gamma(ph_context_t *ctx, float gamma);
```
- **Description**: Sets the gamma correction value.
- **Default**: `2.2`.
- **Constraint**: `gamma > 0.001`.

### 2. Grayscale Color Weights
```c
PH_API void ph_context_set_gray_weights(ph_context_t *ctx, int r, int g, int b);
```
- **Description**: Configures the RGB-to-Grayscale conversion proportions.
- **Normalization**: User-provided weights are **automatically normalized** internally to sum to `128`. This ensures compatibility with the SIMD-optimized fixed-point processing pipeline.
- **Default**: `r=38, g=75, b=15` (ITU-R BT.601 standard).

### 3. pHash (DCT) Parameters
```c
PH_API void ph_context_set_phash_params(ph_context_t *ctx, int dct_size, int reduction_size);
```
- **Description**: Configures the Discrete Cosine Transform resolution.
- **Parameters**: 
    - `dct_size`: Dimension of the input matrix (e.g., 32 for 32x32).
    - `reduction_size`: Number of low-frequency coefficients to keep for the final hash.
- **Constraint**: `reduction_size` is capped at `8` because the standard pHash returns a 64-bit (`uint64_t`) value.
- **Default**: `dct_size=32, reduction_size=8`.

### 4. Radial Hash Parameters
```c
PH_API void ph_context_set_radial_params(ph_context_t *ctx, int projections, int samples);
```
- **Description**: Configures the precision of the Rotation-Resistant Radial Hash.
- **Impact**: The output `ph_digest_t.size` will be equal to `projections` (up to a maximum of 64 bytes).
- **Default**: `projections=40, samples=128`.

### 5. Block-based Hashes (BMH & mHash)
```c
PH_API void ph_context_set_block_params(ph_context_t *ctx, int block_size);
```
- **Description**: Configures the grid resolution (blocks).
- **Impact**: 
    - For **BMH**, the resulting digest size will be `(block_size * block_size) / 8` bytes (max 64 bytes).
    - For **mHash**, it adjusts the edge detection granularity.
- **Default**: `16` (16x16 grid).

---

## Python FFI Integration (ctypes)

For developers building wrappers (e.g., in Python), use the following signatures:

```python
import ctypes

# Assuming 'lib' is the loaded libphash shared library
lib.ph_context_set_gamma.argtypes = [ctypes.c_void_p, ctypes.c_float]
lib.ph_context_set_gray_weights.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
lib.ph_context_set_phash_params.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
lib.ph_context_set_radial_params.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
lib.ph_context_set_block_params.argtypes = [ctypes.c_void_p, ctypes.c_int]
```

## Important Note on Hash Comparability
Hashes generated with different configuration parameters are **not comparable**. Ensure that your entire dataset is hashed using consistent settings for similarity detection to work correctly.
