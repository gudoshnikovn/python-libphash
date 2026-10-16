---
title: "Perceptual image hashing in Python: quick start"
description: "Install python-libphash, hash an image in one line, compare two hashes by Hamming distance and choose among nine perceptual hash algorithms."
---

# Quick start

```bash
pip install python-libphash
```

The wheel carries the C library and its decoders: nothing else is installed or needed.

## Hash an image and compare

```python
import libphash as ph

a = ph.hash("photo.jpg")                   # pHash, a 64-bit int
b = ph.hash("photo_copy.jpg")
ph.hamming_distance(a, b)                  # 0..64 bits differ
ph.similarity(a, b)                        # 1.0 for equal hashes, ~0.5 unrelated
print(ph.hash_to_hex(a))                   # 16 hex digits, for storage
```

A distance of a few bits means the same picture; how many is "a few" depends on the
algorithm and on the edits your copies go through:
[Comparing hashes](https://gudoshnikovn.github.io/libphash/theory/comparing/) on libphash's
site explains how to choose the threshold, and `examples/threshold.py` measures it on
pairs you label.

## Choose an algorithm

`ph.hash()` computes pHash unless told otherwise. Each algorithm is a member of
`Algorithm`, and its libphash name works too:

```python
from libphash import Algorithm

d = ph.hash("photo.jpg", Algorithm.DHASH)  # an int
r = ph.hash("photo.jpg", "radial")         # a Digest
r.similarity(ph.hash("photo_rotated.jpg", "radial"))
```

| Algorithm | How it works | Result | Compare with |
|---|---|---|---|
| `AHASH` | [aHash](https://gudoshnikovn.github.io/libphash/theory/ahash/): an 8×8 thumbnail against its mean | 64-bit `int` | `hamming_distance()`, `similarity()` |
| `DHASH` | [dHash](https://gudoshnikovn.github.io/libphash/theory/dhash/): each cell against its neighbor | 64-bit `int` | `hamming_distance()`, `similarity()` |
| `PHASH` | [pHash](https://gudoshnikovn.github.io/libphash/theory/phash/): the coarsest patterns of the DCT | 64-bit `int` | `hamming_distance()`, `similarity()` |
| `WHASH` | [wHash](https://gudoshnikovn.github.io/libphash/theory/whash/): the Haar wavelet's average | 64-bit `int` | `hamming_distance()`, `similarity()` |
| `BMH` | [BMH](https://gudoshnikovn.github.io/libphash/theory/bmh/): block means against their median | `Digest` of bits | `Digest.hamming_distance()`, `Digest.similarity()` |
| `MHASH` | [mHash](https://gudoshnikovn.github.io/libphash/theory/mhash/): edges through the Marr–Hildreth filter | `Digest` of bits | `Digest.hamming_distance()`, `Digest.similarity()` |
| `RADIAL` | [Radial](https://gudoshnikovn.github.io/libphash/theory/radial/): variance along lines through the center | `Digest` of coefficients | `Digest.similarity()` (peak correlation) |
| `COLOR_HASH` | [ColorHash](https://gudoshnikovn.github.io/libphash/theory/color-hash/): a histogram of coarse colors | `Digest`, a histogram | `Digest.similarity()` (histogram intersection) |
| `COLOR_MOMENTS` | [ColorMoments](https://gudoshnikovn.github.io/libphash/theory/color-moments/): mean, spread and skew per channel | `Digest`, 16-bit features | `Digest.l2_distance()` |

A digest refuses a comparison that does not fit its kind with `DigestKindError`, rather
than return a number that means nothing. Which algorithm suits which use is measured on
libphash's [Choosing an algorithm](https://gudoshnikovn.github.io/libphash/theory/choosing/).

## Several hashes of one image, many images

```python
with ph.ImageContext() as ctx:
    ctx.load_file("photo.jpg")
    hashes = ctx.hashes(Algorithm.PHASH, Algorithm.DHASH, Algorithm.MHASH)
    print(ctx.width, ctx.height, hashes[Algorithm.PHASH])

results = ph.hash_files(["photo.jpg", "photo_copy.jpg", "missing.jpg"])
for r in results:
    print(r.source, r.hashes if r.ok else r.error)
```

A context decodes the image once for all its hashes, and keeps its buffers from one image
to the next; `hash_files()` hashes a list of files on all CPUs, and a file that fails
does not stop the others. [Hashing many images](batch.md) has the details.

## Next

- [Loading images](loading.md): bytes, file objects, numpy, Pillow and OpenCV.
- [Configuring](configuring.md): the settings, and which ones change the hash.
- [Storing and searching](storing.md): hashes in a database, nearest neighbors.
