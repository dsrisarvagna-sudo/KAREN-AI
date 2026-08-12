"""Local OCR for explicitly supplied images."""

from __future__ import annotations

from typing import Any, List, Optional


class OCRInputError(ValueError):
    """Raised when OCR receives no usable image."""


class OCRService:
    """Extract visible text from an image without capturing the screen."""

    def __init__(self, engine: Optional[Any] = None) -> None:
        """Create an OCR service.

        Args:
            engine: Optional compatible OCR engine, primarily useful for tests
                or callers that manage the engine lifecycle themselves.
        """
        self._engine = engine

    def extract(self, image: Any) -> str:
        """Return readable text from ``image`` as newline-separated text.

        The image is processed in memory and is never written to disk. An
        image containing no detectable text returns an empty string.

        Raises:
            OCRInputError: If ``image`` is missing, empty, or unsupported.
            RuntimeError: If the local OCR engine cannot be initialized.
        """
        if image is None:
            raise OCRInputError("An image is required for OCR")

        input_image = self._as_ocr_input(image)
        if input_image is None:
            raise OCRInputError("The supplied image is not a supported image representation")

        try:
            result, _ = self._get_engine()(input_image)
        except OCRInputError:
            raise
        except Exception as exc:
            raise RuntimeError("OCR processing failed") from exc

        if not result:
            return ""
        return "\n".join(
            str(item[1]).strip() for item in result if len(item) > 1 and str(item[1]).strip()
        )

    def _get_engine(self) -> Any:
        if self._engine is None:
            try:
                from rapidocr_onnxruntime import RapidOCR

                self._engine = RapidOCR()
            except Exception as exc:
                raise RuntimeError("The RapidOCR engine is unavailable") from exc
        return self._engine

    @staticmethod
    def _as_ocr_input(image: Any) -> Any:
        """Convert supported in-memory images to a RapidOCR input."""
        if hasattr(image, "rgb") and hasattr(image, "size"):
            # mss.ScreenShot exposes RGB bytes and a (width, height) size.
            width, height = image.size
            if width <= 0 or height <= 0 or not image.rgb:
                return None
            try:
                import numpy as np

                return np.frombuffer(image.rgb, dtype=np.uint8).reshape(height, width, 3)
            except (ImportError, ValueError):
                return None

        if hasattr(image, "convert") and hasattr(image, "mode") and hasattr(image, "size"):
            try:
                import numpy as np

                if image.width <= 0 or image.height <= 0:
                    return None
                return np.asarray(image.convert("RGB"))
            except (ImportError, ValueError):
                return None

        if isinstance(image, (bytes, bytearray)) and not image:
            return None
        if hasattr(image, "size") and image.size == 0:
            return None
        if hasattr(image, "shape") and 0 in image.shape:
            return None
        if isinstance(image, (str, bytes, bytearray)) or hasattr(image, "__array__"):
            return image
        return None
