"""Find the pictures that appear more than once among many files.

Hashes every file with pHash on all CPUs, prints each hash as it would be stored, then
every pair within a threshold, closest first, and the groups those pairs join the files
into. The threshold is the most bits two hashes
of one picture may differ in; measure it on your own images (``threshold.py``). The twin
of libphash's ``examples/find_duplicates.c``: the same files give the same output. Run::

    python examples/find_duplicates.py 7 native/libphash/tests/data/photo.jpeg native/libphash/tests/data/photo_copy.jpeg native/libphash/tests/data/photo.png

prints::

    # algorithm=phash version=2000003 native-jpeg=1
    7eb66192bc394247  native/libphash/tests/data/photo.jpeg
    7eb66192bc394247  native/libphash/tests/data/photo_copy.jpeg
    0100000101000139  native/libphash/tests/data/photo.png
     0 bits  native/libphash/tests/data/photo.jpeg  native/libphash/tests/data/photo_copy.jpeg
    pairs within 7 bits: 1
    group 1: 2 files, widest pair 0 bits
      native/libphash/tests/data/photo.jpeg
      native/libphash/tests/data/photo_copy.jpeg
    groups: 1
"""

from __future__ import annotations

import sys
from itertools import combinations

import libphash as ph


def find(parent: list[int], i: int) -> int:
    """Return the group of file ``i``: the file its chain of parents ends at, the first."""
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(f"usage: {argv[0]} <max-bits> <image>...", file=sys.stderr)
        return 1
    try:
        max_bits = int(argv[1])
    except ValueError:
        max_bits = -1
    if not 0 <= max_bits <= 64:
        print("max-bits must be a number from 0 to 64", file=sys.stderr)
        return 1

    # Every file hashed with pHash on all CPUs; a file that cannot be read fails alone.
    results = ph.hash_files(argv[2:], ph.Algorithm.PHASH)

    # A stored hash carries what decides its value: the algorithm, the library version,
    # and whether JPEG went through libjpeg-turbo or stb_image. The settings are the
    # defaults here; a program that changes them stores them too.
    major, minor, patch = (int(n) for n in ph.libphash_version().split("."))
    version = major * 1_000_000 + minor * 1000 + patch
    jpeg = int(ph.can_decode("jpeg"))
    print(f"# algorithm={ph.Algorithm.PHASH} version={version} native-jpeg={jpeg}")
    hashed: list[tuple[str, int]] = []
    for result in results:
        if result.hashes is None:
            print(result.error, file=sys.stderr)
        else:
            value = result.hashes[ph.Algorithm.PHASH]
            print(f"{ph.hash_to_hex(value)}  {result.source}")
            hashed.append((result.source, value))

    # Every pair compared once: n * (n - 1) / 2 Hamming distances.
    pairs = [
        (distance, i, j)
        for i, j in combinations(range(len(hashed)), 2)
        if (distance := ph.hamming_distance(hashed[i][1], hashed[j][1])) <= max_bits
    ]
    for distance, i, j in sorted(pairs, key=lambda p: p[0]):
        print(f"{distance:2d} bits  {hashed[i][0]}  {hashed[j][0]}")
    print(f"pairs within {max_bits} bits: {len(pairs)}")

    # Each pair joins the groups of its two files, so a group holds every file a chain of
    # pairs connects, and is known by its first file: the groups come in the order of
    # their first files. Two files of one group may be further apart than the threshold;
    # its widest pair says how far.
    parent = list(range(len(hashed)))
    for _, i, j in pairs:
        a, b = find(parent, i), find(parent, j)
        parent[max(a, b)] = min(a, b)
    groups: dict[int, list[int]] = {}
    for i in range(len(hashed)):
        groups.setdefault(find(parent, i), []).append(i)
    copies = [group for group in groups.values() if len(group) > 1]
    for number, group in enumerate(copies, 1):
        widest = max(
            ph.hamming_distance(hashed[i][1], hashed[j][1])
            for i, j in combinations(group, 2)
        )
        print(f"group {number}: {len(group)} files, widest pair {widest} bits")
        for i in group:
            print(f"  {hashed[i][0]}")
    print(f"groups: {len(copies)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
