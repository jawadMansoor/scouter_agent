# coverage_view.py  (put at repo root or wherever convenient)

"""
Display a bitmap of scouted tiles saved in coverage.npy
Green  = covered,  Black = hole.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse

def main(path: Path):
    bitmap = np.load(path)
    plt.figure(figsize=(6,6))
    plt.imshow(bitmap, cmap="Greens", interpolation="none", origin="lower")
    plt.title(f"Coverage map ({bitmap.shape[0]}×{bitmap.shape[1]} tiles)")
    plt.xlabel("Columns"); plt.ylabel("Rows")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="coverage.npy path", type=Path)
    main(parser.parse_args().file)
