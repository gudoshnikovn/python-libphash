import os
import glob
from cffi import FFI

ffibuilder = FFI()

# 1. Define the C definitions exposed to Python
# We strip macros like PH_API for CFFI parsing
ffibuilder.cdef("""
    // Constants
    #define PH_DIGEST_MAX_BYTES 64

    // Error Codes
    typedef enum {
        PH_SUCCESS = 0,
        PH_ERR_ALLOCATION_FAILED = -1,
        PH_ERR_DECODE_FAILED = -2,
        PH_ERR_INVALID_ARGUMENT = -3,
        PH_ERR_EMPTY_IMAGE = -5,
        ...
    } ph_error_t;

    typedef enum {
        PH_WHASH_FAST = 0,
        PH_WHASH_FULL = 1,
        ...
    } ph_whash_mode_t;

    // Types
    typedef struct ph_context ph_context_t;

    typedef struct {
        uint8_t data[PH_DIGEST_MAX_BYTES];
        uint8_t size;
        uint8_t reserved[7];
    } ph_digest_t;

    // Lifecycle
    const char *ph_version(void);
    ph_error_t ph_create(ph_context_t **out_ctx);
    void ph_free(ph_context_t *ctx);
    void ph_context_set_gamma(ph_context_t *ctx, float gamma);
    void ph_context_set_gray_weights(ph_context_t *ctx, int r, int g, int b);
    void ph_context_set_phash_params(ph_context_t *ctx, int dct_size, int reduction_size);
    void ph_context_set_radial_params(ph_context_t *ctx, int projections, int samples);
    void ph_context_set_block_params(ph_context_t *ctx, int block_size);
    void ph_context_set_load_grayscale(ph_context_t *ctx, int enable);
    void ph_context_set_whash_mode(ph_context_t *ctx, ph_whash_mode_t mode);

    int ph_can_use_libjpeg(void);
    int ph_can_use_libpng(void);

    // Loading
    ph_error_t ph_load_from_file(ph_context_t *ctx, const char *filepath);
    ph_error_t ph_load_from_memory(ph_context_t *ctx, const uint8_t *buffer, size_t length);

    // uint64 Hashes
    ph_error_t ph_compute_ahash(ph_context_t *ctx, uint64_t *out_hash);
    ph_error_t ph_compute_dhash(ph_context_t *ctx, uint64_t *out_hash);
    ph_error_t ph_compute_phash(ph_context_t *ctx, uint64_t *out_hash);
    ph_error_t ph_compute_whash(ph_context_t *ctx, uint64_t *out_hash);
    ph_error_t ph_compute_mhash(ph_context_t *ctx, uint64_t *out_hash);
    ph_error_t ph_compute_color_hash(ph_context_t *ctx, uint64_t *out_hash);

    // Digest Hashes
    ph_error_t ph_compute_bmh(ph_context_t *ctx, ph_digest_t *out_digest);
    ph_error_t ph_compute_color_moments_hash(ph_context_t *ctx, ph_digest_t *out_digest);
    ph_error_t ph_compute_radial_hash(ph_context_t *ctx, ph_digest_t *out_digest);

    // Comparison
    int ph_hamming_distance(uint64_t hash1, uint64_t hash2);
    int ph_hamming_distance_digest(const ph_digest_t *a, const ph_digest_t *b);
    double ph_l2_distance(const ph_digest_t *a, const ph_digest_t *b);
""")

# 2. Configure the Source Compilation
curr_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(curr_dir, "../../"))
native_dir = os.path.join(project_root, "native", "libphash")

# --- Build Configuration (Environment Variables) ---
# LIBPHASH_MINIMAL=1          → stb_image only, zero deps
# LIBPHASH_NO_TURBOJPEG=1     → skip TurboJPEG
# LIBPHASH_NO_LIBPNG=1        → skip libpng
is_minimal = os.environ.get("LIBPHASH_MINIMAL", "0") == "1"
use_turbojpeg = not is_minimal and os.environ.get("LIBPHASH_NO_TURBOJPEG", "0") != "1"
use_libpng = not is_minimal and os.environ.get("LIBPHASH_NO_LIBPNG", "0") != "1"

extra_compile_defs = []
extra_include_dirs = []
extra_link_libs = []
extra_link_args = []
extra_libs = ["m"] if os.name == "posix" else []

# --- Build libjpeg-turbo (static, optional) ---
if use_turbojpeg:
    turbojpeg_dir = os.path.join(native_dir, "vendor", "libjpeg-turbo")
    turbojpeg_build = os.path.join(turbojpeg_dir, "build")
    turbojpeg_lib = os.path.join(turbojpeg_build, "libturbojpeg.a")

    if not os.path.exists(turbojpeg_lib):
        import subprocess
        import multiprocessing

        # libjpeg-turbo 3.x+ requires nasm >= 2.14 for SIMD.
        # Manylinux2014 i686 images have nasm 2.10.x which is too old.
        # We disable SIMD on i386/i686 to ensure build stability.
        is_i386 = platform.machine() in ("i386", "i686", "x86")
        simd_opt = os.environ.get("LIBPHASH_WITH_SIMD", "OFF" if is_i386 else "ON")

        os.makedirs(turbojpeg_build, exist_ok=True)
        subprocess.check_call(
            [
                "cmake",
                "..",
                "-DCMAKE_BUILD_TYPE=Release",
                "-DENABLE_SHARED=OFF",
                "-DENABLE_STATIC=ON",
                "-DWITH_TURBOJPEG=ON",
                f"-DWITH_SIMD={simd_opt}",
                "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
            ],
            cwd=turbojpeg_build,
        )
        subprocess.check_call(
            ["make", f"-j{multiprocessing.cpu_count()}"], cwd=turbojpeg_build
        )

    extra_compile_defs.append("-DPH_USE_TURBOJPEG")
    extra_include_dirs.append(
        os.path.relpath(os.path.join(turbojpeg_dir, "src"), project_root)
    )
    extra_include_dirs.append(os.path.relpath(turbojpeg_build, project_root))
    extra_link_args.append(os.path.relpath(turbojpeg_lib, project_root))

# --- PNG decoder: auto-select based on platform ---
# ARM (Mac) → libpng (NEON filters are faster)
# x86 (Linux) → spng (43% faster inflate pipeline)
# Override: LIBPHASH_USE_SPNG=1 or LIBPHASH_USE_LIBPNG=1
import platform

is_arm = platform.machine() in ("arm64", "aarch64")

use_spng = os.environ.get("LIBPHASH_USE_SPNG", "0") == "1"
use_libpng_forced = os.environ.get("LIBPHASH_USE_LIBPNG", "0") == "1"

if is_minimal:
    use_spng = False
    use_libpng = False
elif use_spng:
    use_libpng = False
elif use_libpng_forced:
    use_libpng = True
    use_spng = False
elif is_arm:
    # ARM: use libpng by default (NEON optimized)
    use_libpng = True
    use_spng = False
else:
    # x86: use spng by default (faster inflate)
    use_libpng = False
    use_spng = True

if use_libpng:
    libpng_dir = os.path.join(native_dir, "vendor", "libpng")
    libpng_build = os.path.join(libpng_dir, "build")
    libpng_lib = os.path.join(libpng_build, "libpng16.a")

    if not os.path.exists(libpng_lib):
        import subprocess
        import multiprocessing

        os.makedirs(libpng_build, exist_ok=True)
        subprocess.check_call(
            [
                "cmake",
                "..",
                "-DCMAKE_BUILD_TYPE=Release",
                "-DPNG_SHARED=OFF",
                "-DPNG_STATIC=ON",
                "-DPNG_TESTS=OFF",
                "-DPNG_HARDWARE_OPTIMIZATIONS=ON",
                "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
            ],
            cwd=libpng_build,
        )
        subprocess.check_call(
            ["make", f"-j{multiprocessing.cpu_count()}"], cwd=libpng_build
        )

    extra_compile_defs.append("-DPH_USE_LIBPNG")
    extra_include_dirs.append(os.path.relpath(libpng_dir, project_root))
    extra_include_dirs.append(os.path.relpath(libpng_build, project_root))
    extra_link_args.append(os.path.relpath(libpng_lib, project_root))
    extra_libs.append("z")

elif use_spng:
    # spng is a single .c file, compiled alongside our sources
    spng_dir = os.path.join(native_dir, "vendor", "spng", "spng")
    extra_compile_defs.append("-DPH_USE_SPNG")
    extra_include_dirs.append(os.path.relpath(spng_dir, project_root))
    extra_libs.append("z")

# --- Collect sources ---
sources = []
sources.extend(glob.glob(os.path.join(native_dir, "src", "*.c")))
sources.extend(glob.glob(os.path.join(native_dir, "src", "hashes", "*.c")))

# spng is a single .c file compiled alongside our sources
if use_spng:
    spng_src = os.path.join(native_dir, "vendor", "spng", "spng", "spng.c")
    sources.append(spng_src)

source_files = [os.path.relpath(s, project_root) for s in sources]
include_dirs = [
    os.path.relpath(os.path.join(native_dir, "include"), project_root),
] + extra_include_dirs

compile_args = (
    ["-O3", "-Wall", "-fPIC"] if os.name == "posix" else ["/O2", "/W3"]
) + extra_compile_defs

ffibuilder.set_source(
    "libphash._native",
    '#include "libphash.h"',
    sources=source_files,
    include_dirs=include_dirs,
    libraries=extra_libs,
    extra_compile_args=compile_args,
    extra_link_args=extra_link_args,
)
if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
