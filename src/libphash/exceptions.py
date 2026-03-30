from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._native import lib
else:
    try:
        from ._native import lib
    except ImportError:
        lib = None


class PhashError(Exception):
    """Base exception for libphash library."""


class AllocationError(PhashError):
    """Raised when memory allocation fails in the C layer."""


class DecodeError(PhashError):
    """Raised when image decoding fails (stb_image error)."""


class InvalidArgumentError(PhashError):
    """Raised when an invalid argument is passed to the C function."""


class NotImplementedError(PhashError):
    """Raised when a feature is not implemented or disabled at compile-time."""


class EmptyImageError(PhashError):
    """Raised when an operation is requested on an empty context."""


def check_error(err_code: int) -> None:
    """Map C return codes to Python exceptions."""
    if err_code == 0:
        return

    errors: dict[int, type[PhashError]] = {
        -1: AllocationError,
        -2: DecodeError,
        -3: InvalidArgumentError,
        -4: NotImplementedError,
        -5: EmptyImageError,
    }

    exc_class = errors.get(err_code, PhashError)

    # Use C engine to get human-readable error string if available
    msg = None
    if lib is not None:
        try:
            c_str = lib.ph_get_error_string(err_code)
            from ._native import ffi

            msg = ffi.string(c_str).decode()
        except Exception:
            pass

    if not msg:
        # Fallback messages
        fallback_msgs = {
            -1: "Memory allocation failed in libphash",
            -2: "Failed to decode image",
            -3: "Invalid argument provided to libphash",
            -4: "Feature not implemented",
            -5: "Image is empty or invalid",
        }
        msg = fallback_msgs.get(err_code, f"Unknown error code: {err_code}")

    raise exc_class(msg)
