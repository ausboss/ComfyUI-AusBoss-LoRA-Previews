"""Save a LoRA's preview picture next to the LoRA file.

The browser downloads the picture from Civitai and sends the bytes here. This
side only checks them and writes one small JPEG beside the LoRA. It makes no
network requests, runs no programs, and never replaces a picture that is
already there.
"""

from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path

try:
    import folder_paths
except ImportError:  # pragma: no cover - only outside ComfyUI
    folder_paths = None

# The names a preview picture can have next to a LoRA, the same list the
# AusBoss LoRA Loader looks for. If any of them exists, nothing is saved.
PREVIEW_SUFFIXES = (".preview.png", ".preview.jpg", ".preview.jpeg", ".preview.webp",
                    ".png", ".jpg", ".jpeg", ".webp")
SAVED_SUFFIX = ".preview.jpg"

MAX_BYTES = 8 * 1024 * 1024
MAX_PIXELS = 40_000_000
LONG_EDGE = 768
JPEG_QUALITY = 88


class PreviewError(ValueError):
    """A problem whose message is safe to show to the person."""


def lora_path(name: object) -> Path:
    """The LoRA file for a name ComfyUI lists in its loras folders."""
    if folder_paths is None:
        raise PreviewError("ComfyUI's folders are not available.")
    if not isinstance(name, str) or not name:
        raise PreviewError("No LoRA name was given.")
    if name not in folder_paths.get_filename_list("loras"):
        raise PreviewError("That LoRA is not in ComfyUI's loras folders.")
    full = folder_paths.get_full_path("loras", name)
    if not full:
        raise PreviewError("That LoRA is not in ComfyUI's loras folders.")
    path = Path(os.path.abspath(full))
    roots = [Path(os.path.abspath(root)) for root in folder_paths.get_folder_paths("loras")]
    if not any(root in path.parents for root in roots):
        raise PreviewError("That LoRA is not in ComfyUI's loras folders.")
    return path


def existing_preview(path: Path) -> Path | None:
    stem = str(path.with_suffix(""))
    for suffix in PREVIEW_SUFFIXES:
        candidate = Path(stem + suffix)
        if candidate.is_file():
            return candidate
    return None


def has_preview(name: object) -> bool:
    return existing_preview(lora_path(name)) is not None


def make_jpeg(data: bytes) -> bytes:
    """The picture as a JPEG no larger than LONG_EDGE, with no metadata."""
    if not data:
        raise PreviewError("The picture is empty.")
    if len(data) > MAX_BYTES:
        raise PreviewError("The picture is too large.")
    from PIL import Image, UnidentifiedImageError

    try:
        with Image.open(BytesIO(data)) as image:
            width, height = image.size
            if width < 1 or height < 1 or width * height > MAX_PIXELS:
                raise PreviewError("The picture is too large.")
            picture = image.convert("RGB")
    except PreviewError:
        raise
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
        raise PreviewError("That is not a picture this add-on can read.") from None
    picture.thumbnail((LONG_EDGE, LONG_EDGE))
    out = BytesIO()
    picture.save(out, "JPEG", quality=JPEG_QUALITY)
    return out.getvalue()


def save_preview(name: object, data: bytes) -> Path:
    """Write <lora>.preview.jpg next to the LoRA. Never overwrites."""
    path = lora_path(name)
    if existing_preview(path) is not None:
        raise PreviewError("This LoRA already has a preview picture.")
    jpeg = make_jpeg(data)
    target = Path(str(path.with_suffix("")) + SAVED_SUFFIX)
    try:
        with open(target, "xb") as handle:
            handle.write(jpeg)
    except FileExistsError:
        raise PreviewError("This LoRA already has a preview picture.") from None
    return target


def safe_message(error: Exception) -> str:
    if isinstance(error, PreviewError):
        return str(error)
    return "Could not save the preview picture."
