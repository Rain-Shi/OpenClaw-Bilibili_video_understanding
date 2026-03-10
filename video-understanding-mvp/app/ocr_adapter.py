from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .asr_adapter import shutil_which


class OCRAdapterError(RuntimeError):
    pass


def load_mock_or_existing_ocr(frame_path: str) -> List[str]:
    sidecar = Path(frame_path).with_suffix('.ocr.json')
    if sidecar.exists():
        try:
            data = json.loads(sidecar.read_text())
            if isinstance(data, list):
                return [str(x) for x in data]
        except Exception:
            pass
    return []


def extract_ocr_text(frame_path: str) -> List[str]:
    """Graceful OCR hook.

    Current behavior:
    - if OCR dependencies are not installed, fallback to sidecar/mock OCR
    - later this can be upgraded to pytesseract / paddleocr / cloud OCR
    """
    # We only check binary presence for now; python OCR deps are not installed in this env.
    if not shutil_which('tesseract'):
        return load_mock_or_existing_ocr(frame_path)

    # Placeholder for future real OCR implementation.
    # Keep fallback deterministic for now.
    return load_mock_or_existing_ocr(frame_path)
