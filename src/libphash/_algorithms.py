from __future__ import annotations

from enum import IntEnum
from typing import Union

from ._errors import PH_SUCCESS
from ._native import ffi, lib
from ._sources import encode_text
from .exceptions import InvalidArgumentError


class Algorithm(IntEnum):
    """A hash algorithm; the values are libphash's ``ph_algorithm_t``.

    Wherever an algorithm is expected, its libphash name (``"phash"``,
    ``"color_moments"``) is accepted too; ``str(algorithm)`` is that name. How each one
    works and what it survives is on libphash's site, one page per algorithm, and
    [Choosing an algorithm](https://gudoshnikovn.github.io/libphash/theory/choosing/)
    sets them side by side.
    """

    # Literal values, so that type checkers see the members (libphash never changes an
    # existing value; the tests compare them with the C enum).

    #: [aHash][ahash], the average hash: each cell of an 8-by-8 thumbnail against
    #: their mean. A 64-bit ``int``.
    #:
    #: [ahash]: https://gudoshnikovn.github.io/libphash/theory/ahash/
    AHASH = 0
    #: [dHash][dhash], the difference hash: each cell of a 9-by-8 thumbnail against
    #: its neighbor. A 64-bit ``int``.
    #:
    #: [dhash]: https://gudoshnikovn.github.io/libphash/theory/dhash/
    DHASH = 1
    #: [pHash][phash], the perceptual hash and the default: the coarsest cosine
    #: patterns of the DCT. A 64-bit ``int``.
    #:
    #: [phash]: https://gudoshnikovn.github.io/libphash/theory/phash/
    PHASH = 2
    #: [wHash][whash], the wavelet hash: the Haar wavelet's average against its
    #: median. A 64-bit ``int``.
    #:
    #: [whash]: https://gudoshnikovn.github.io/libphash/theory/whash/
    WHASH = 3
    #: [BMH][bmh], the block mean hash: a grid of block means against their
    #: median. A ``Digest`` of bits.
    #:
    #: [bmh]: https://gudoshnikovn.github.io/libphash/theory/bmh/
    BMH = 4
    #: [mHash][mhash], the Marr-Hildreth hash: edges and detail through the
    #: Mexican-hat filter. A ``Digest`` of bits.
    #:
    #: [mhash]: https://gudoshnikovn.github.io/libphash/theory/mhash/
    MHASH = 5
    #: [Radial][radial], the radial variance hash: the variance along lines through
    #: the center, which survives rotation. A ``Digest`` of coefficients.
    #:
    #: [radial]: https://gudoshnikovn.github.io/libphash/theory/radial/
    RADIAL = 6
    #: [ColorHash][color-hash], a histogram of which colors the picture is made of.
    #: A ``Digest`` histogram.
    #:
    #: [color-hash]: https://gudoshnikovn.github.io/libphash/theory/color-hash/
    COLOR_HASH = 7
    #: [ColorMoments][color-moments], the mean, spread and skew of each color channel.
    #: A ``Digest`` of 16-bit features.
    #:
    #: [color-moments]: https://gudoshnikovn.github.io/libphash/theory/color-moments/
    COLOR_MOMENTS = 8

    def __str__(self) -> str:
        return str(ffi.string(lib.ph_algorithm_name(self.value)).decode())


class DigestKind(IntEnum):
    """What a digest's bytes mean, and so which comparisons it supports.

    The values are those of ``ph_digest_kind_t``.
    """

    UNSPECIFIED = 0
    BITS = 1
    COEFFICIENTS = 2
    VECTOR = 3
    HISTOGRAM = 4
    VECTOR16 = 5


AlgorithmLike = Union["Algorithm", str]

#: The algorithms that produce a 64-bit integer; the others produce a Digest.
UINT64_ALGORITHMS = frozenset(
    Algorithm[name] for name in ("AHASH", "DHASH", "PHASH", "WHASH")
)


def to_algorithm(value: object) -> Algorithm:
    if isinstance(value, Algorithm):
        return value
    if isinstance(value, str):
        out = ffi.new("ph_algorithm_t *")
        if lib.ph_algorithm_from_name(encode_text(value), out) != PH_SUCCESS:
            names = ", ".join(str(a) for a in Algorithm)
            raise InvalidArgumentError(
                f"unknown algorithm {value!r}; expected one of {names}"
            )
        return Algorithm(int(out[0]))
    if isinstance(value, int) and not isinstance(value, bool):
        try:
            return Algorithm(value)
        except ValueError:
            pass
    raise InvalidArgumentError(f"expected an Algorithm or its name, got {value!r}")


def uint64_flags(algorithms: list[Algorithm]) -> int:
    """Return the ph_hash_flags_t bits of uint64 algorithms: bit ``1 << value``."""
    flags = 0
    for algo in algorithms:
        if algo not in UINT64_ALGORITHMS:
            names = ", ".join(str(a) for a in sorted(UINT64_ALGORITHMS))
            raise InvalidArgumentError(
                f"{algo} produces a digest; only {names} "
                "can be computed together or in a batch"
            )
        flags |= 1 << int(algo)
    return flags
