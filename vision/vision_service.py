"""Vision model access with bounded, in-memory image preprocessing."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Optional

from PIL import Image


class VisionInputError(ValueError):
    """Raised when the vision service receives no usable image."""


class VisionService:
    """Prepare an image and request a concise description from Qwen2.5-VL."""

    MODEL = "qwen2.5vl:3b"
    DEFAULT_PROMPT = (
        "Describe what is visible on this screen. Identify the main application, "
        "important UI elements, and readable text. Be concise."
    )

    def __init__(self, max_dimension: int = 1024, client: Optional[Any] = None) -> None:
        if max_dimension <= 0:
            raise ValueError("max_dimension must be greater than zero")
        self.max_dimension = max_dimension
        self._client = client

    def describe(self, image: Any, prompt: Optional[str] = None) -> str:
        """Return a model description of ``image``.

        The original image is never resized or otherwise changed. The API receives
        only the processed image bytes, not a path embedded in the prompt.
        """
        processed = self.preprocess(image)
        image_bytes = self._png_bytes(processed)
        request_prompt = prompt or self.DEFAULT_PROMPT

        try:
            response = self._get_client().chat(
                model=self.MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": request_prompt,
                        "images": [image_bytes],
                    }
                ],
            )
        except Exception as exc:
            raise RuntimeError("Vision model request failed") from exc

        try:
            if isinstance(response, dict):
                return str(response["message"]["content"])
            return str(response.message.content)
        except (AttributeError, KeyError, TypeError) as exc:
            raise RuntimeError("Vision model returned an invalid response") from exc

    def preprocess(self, image: Any) -> Image.Image:
        """Return a copied RGB image resized within ``max_dimension``."""
        source = self._as_pil_image(image)
        width, height = source.size
        if width <= 0 or height <= 0:
            raise VisionInputError("The supplied image has no usable dimensions")

        result = source.copy()
        largest_dimension = max(result.size)
        if largest_dimension > self.max_dimension:
            scale = self.max_dimension / largest_dimension
            resized = (
                max(1, round(result.width * scale)),
                max(1, round(result.height * scale)),
            )
            result = result.resize(resized, Image.Resampling.LANCZOS)
        return result

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import ollama

                self._client = ollama
            except Exception as exc:
                raise RuntimeError("The Python ollama package is unavailable") from exc
        return self._client

    @staticmethod
    def _png_bytes(image: Image.Image) -> bytes:
        output = BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()

    @staticmethod
    def _as_pil_image(image: Any) -> Image.Image:
        if image is None:
            raise VisionInputError("An image is required for vision description")

        try:
            if isinstance(image, (str, Path)):
                with Image.open(image) as opened:
                    return opened.convert("RGB")
            if hasattr(image, "rgb") and hasattr(image, "size"):
                width, height = image.size
                return Image.frombytes("RGB", (width, height), image.rgb)
            if isinstance(image, Image.Image):
                return image.convert("RGB")
            if hasattr(image, "__array__"):
                import numpy as np

                return Image.fromarray(np.asarray(image)).convert("RGB")
        except (OSError, TypeError, ValueError) as exc:
            raise VisionInputError("The supplied image is not supported") from exc

        raise VisionInputError("The supplied image is not supported")
