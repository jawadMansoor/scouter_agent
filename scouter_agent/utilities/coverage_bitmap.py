# scouter_agent/utilities/coverage_bitmap.py
from __future__ import annotations
import numpy as np
from pathlib import Path
from typing import Iterable, Tuple

class CoverageBitmap:
    """Tiny 8‑bit bitmap: 1 = tile covered, 0 = hole."""
    def __init__(self, rows: int = 1200, cols: int = 1200) -> None:
        self.rows, self.cols = rows, cols
        self.map = np.zeros((rows, cols), dtype=np.uint8)

    # ------------------------------------------------------------------
    def mark(self, tiles: Iterable[Tuple[int, int]]) -> None:
        for r, c in tiles:
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.map[r, c] = 1

    # ------------------------------------------------------------------
    def holes(self) -> np.ndarray:
        rr, cc = np.where(self.map == 0)
        return np.stack([rr, cc], axis=1)

    # ------------------------------------------------------------------
    def save(self, path: Path) -> None:
        np.save(path, self.map)

    @classmethod
    def load(cls, path: Path) -> "CoverageBitmap":
        obj = cls(*np.load(path).shape)
        obj.map = np.load(path)
        return obj
