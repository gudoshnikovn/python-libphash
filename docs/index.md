---
title: "python-libphash: perceptual image hashing for Python"
description: "Perceptual image hashing for Python: pHash, dHash, aHash, wHash and five more algorithms in C, to find duplicate and near-duplicate images quickly."
hide:
  - navigation
---

# python-libphash

**Perceptual image hashing in Python**, with the [libphash](https://gudoshnikovn.github.io/libphash/)
C library inside. A perceptual hash changes little when an image is resized,
recompressed or slightly edited, so comparing hashes finds the copies of a picture among
many images; an unrelated picture lands about half the bits away.

```python
import libphash as ph

original = ph.hash("photo.jpg")            # pHash: a 64-bit int
copy = ph.hash("photo_copy.jpg")
ph.hamming_distance(original, copy)        # bits that differ: 0 for a copy
```

The package computes nine algorithms in C (pHash, dHash, aHash, wHash, BMH, mHash,
Radial, ColorHash and ColorMoments), decodes JPEG, PNG and WebP with libraries linked
into the wheel, and gives the same hash for the same file on Linux, macOS and Windows, on
x86-64 and arm64. Its hashes are libphash's, bit for bit: a collection can be hashed
partly from C and partly from Python.

It installs as `python-libphash` and imports as `libphash`. libphash is its own C
library, not pHash.org's (which Debian and Ubuntu package as `libphash0`), and the
package depends on neither that library nor `imagehash`, numpy or OpenCV.

<div class="grid cards" markdown>

-   **Start**

    ---

    Install the wheel, hash and compare your first images.

    [Quick start](guide/quickstart.md)

-   **Many images**

    ---

    Hash a directory on all CPUs, store the hashes and find the duplicates.

    [Hashing many images](guide/batch.md) · [Storing and searching](guide/storing.md) ·
    [Command line](guide/cli.md)

-   **Pick an algorithm and a threshold**

    ---

    What each of the nine algorithms survives, and how far apart copies land: the
    theory and the measurements are on libphash's site.

    [Choosing an algorithm](https://gudoshnikovn.github.io/libphash/theory/choosing/)

-   **API reference**

    ---

    Every function, class and exception, from the docstrings.

    [API reference](api/index.md)

</div>

## What a perceptual hash is for

Hashes are deterministic and unkeyed. They find the copies of a picture in a collection
you control: duplicates in a photo library, the same product image uploaded twice,
re-encoded frames. They are not for moderation, blocklists or checking untrusted input:
anyone who can choose the images can make two different pictures hash alike, or alter
a picture until its hash no longer matches. libphash's page
[What a perceptual hash is not](https://gudoshnikovn.github.io/libphash/theory/perceptual-hashing/#what-a-perceptual-hash-is-not)
explains why no perceptual hash is fit for that.
