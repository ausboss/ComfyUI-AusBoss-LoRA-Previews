"""Run with: python tests/test_previews.py (Pillow must be installed)."""

from __future__ import annotations

import sys
import tempfile
import types
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


class FakeFolders(types.ModuleType):
    def __init__(self, root: Path):
        super().__init__("folder_paths")
        self.root = root

    def get_folder_paths(self, kind):
        return [str(self.root)] if kind == "loras" else []

    def get_filename_list(self, kind):
        if kind != "loras":
            return []
        return sorted(str(p.relative_to(self.root)).replace("\\", "/")
                      for p in self.root.rglob("*.safetensors"))

    def get_full_path(self, kind, name):
        path = self.root / name
        return str(path) if path.is_file() else None


def picture(width=1200, height=800, mode="RGB", fmt="PNG") -> bytes:
    out = BytesIO()
    Image.new(mode, (width, height), 120 if mode == "L" else (200, 40, 60)[:len(mode)] + (255,) * (len(mode) - 3)).save(out, fmt)
    return out.getvalue()


class SavePreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "loras"
        (self.root / "styles").mkdir(parents=True)
        (self.root / "styles" / "ink.v2.safetensors").write_bytes(b"x")
        sys.modules["folder_paths"] = FakeFolders(self.root)
        sys.path.insert(0, str(ROOT))
        import previews
        self.previews = previews
        previews.folder_paths = sys.modules["folder_paths"]

    def tearDown(self):
        self.tmp.cleanup()
        sys.path.remove(str(ROOT))
        sys.modules.pop("folder_paths", None)

    def test_saves_a_small_jpeg_next_to_the_lora(self):
        target = self.previews.save_preview("styles/ink.v2.safetensors", picture())
        self.assertEqual(target, self.root / "styles" / "ink.v2.preview.jpg")
        with Image.open(target) as saved:
            self.assertEqual(saved.format, "JPEG")
            self.assertEqual(max(saved.size), self.previews.LONG_EDGE)
            self.assertFalse(saved.info.get("exif"))
        self.assertTrue(self.previews.has_preview("styles/ink.v2.safetensors"))

    def test_never_replaces_a_picture_that_is_there(self):
        own = self.root / "styles" / "ink.v2.png"
        own.write_bytes(picture(10, 10))
        with self.assertRaises(self.previews.PreviewError):
            self.previews.save_preview("styles/ink.v2.safetensors", picture())
        self.assertFalse((self.root / "styles" / "ink.v2.preview.jpg").exists())
        self.assertEqual(own.read_bytes(), picture(10, 10))

    def test_only_listed_loras(self):
        for name in ["../outside.safetensors", "styles/missing.safetensors", "", None, 5]:
            with self.assertRaises(self.previews.PreviewError, msg=repr(name)):
                self.previews.save_preview(name, picture())

    def test_refuses_what_is_not_a_picture_or_is_too_large(self):
        name = "styles/ink.v2.safetensors"
        for data in [b"", b"not a picture", b"\x89PNG\r\n\x1a\n broken"]:
            with self.assertRaises(self.previews.PreviewError):
                self.previews.save_preview(name, data)
        with self.assertRaises(self.previews.PreviewError):
            self.previews.save_preview(name, b"x" * (self.previews.MAX_BYTES + 1))
        with self.assertRaises(self.previews.PreviewError):
            self.previews.make_jpeg(picture(8000, 6000, mode="L"))
        self.assertFalse((self.root / "styles" / "ink.v2.preview.jpg").exists())

    def test_reads_webp_and_pictures_with_transparency(self):
        jpeg = self.previews.make_jpeg(picture(300, 200, mode="RGBA", fmt="WEBP"))
        with Image.open(BytesIO(jpeg)) as saved:
            self.assertEqual((saved.format, saved.size), ("JPEG", (300, 200)))

    def test_error_text_names_no_path(self):
        self.assertEqual(self.previews.safe_message(OSError("/secret/place")), "Could not save the preview picture.")


if __name__ == "__main__":
    unittest.main()
