"""
Fifteen structural coordinates for inspection images (SEM, wafer maps, aerial images).

The math lives in `_v31.py`, a verbatim copy of the research extractor (released
internally as "VTL v3.1, Visual Topology of Light"). This module gives the
coordinates the names inspection engineers use and handles image loading.
Numbers are pinned by tests/test_golden.py.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Union

import numpy as np
import pandas as pd
from PIL import Image

from . import _v31

VERSION = "inspection-coordinates-v3.1"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

# research name -> public name
NAMES: Dict[str, str] = {
    "delta_x": "centroid_offset_x",
    "delta_y": "centroid_offset_y",
    "r_v": "radial_variance",
    "mu": "mean_intensity",
    "sdi": "intensity_entropy",
    "rho_r": "radial_intensity_correlation",
    "x_p": "peak_offset_x",
    "theta": "dominant_orientation",
    "d_s": "spectral_centroid",
    "nils": "image_log_slope",
    "ler": "edge_roughness",
    "edge_density": "edge_density",
    "ds_low": "spectral_power_low",
    "ds_mid": "spectral_power_mid",
    "ds_high": "spectral_power_high",
}
COORDINATES: Tuple[str, ...] = tuple(NAMES[k] for k in _v31.COORD_NAMES)

ImageLike = Union[str, os.PathLike, Image.Image, np.ndarray]


def load_gray(image: ImageLike) -> np.ndarray:
    """Grayscale uint8 array. Files and PIL images go through PIL `convert("L")`,
    as in the published benchmarks; arrays are used as given (color is averaged)."""
    if isinstance(image, np.ndarray):
        return image
    if isinstance(image, Image.Image):
        return np.array(image.convert("L"))
    return np.array(Image.open(image).convert("L"))


def measure(image: ImageLike) -> Dict[str, float]:
    """The fifteen coordinates for one image, under their public names."""
    raw = _v31.extract(load_gray(image))
    return {NAMES[k]: raw[k] for k in _v31.COORD_NAMES}


def measure_raw(image: ImageLike) -> Dict[str, float]:
    """The same coordinates under the research names (delta_x, r_v, nils…)."""
    return _v31.extract(load_gray(image))


def find_images(*paths: Union[str, os.PathLike]) -> List[Tuple[Path, str]]:
    """(path, relative name) for image files and folders (recursive, hidden skipped)."""
    found = {}
    for p in map(Path, paths):
        if p.is_dir():
            for q in p.rglob("*"):
                rel = q.relative_to(p)
                if q.suffix.lower() in IMAGE_EXTS and not any(s.startswith(".") for s in rel.parts):
                    found.setdefault(q, rel.as_posix())
        elif p.suffix.lower() in IMAGE_EXTS:
            found.setdefault(p, p.name)
    return sorted(found.items())


def measure_many(paths: Union[str, os.PathLike, Iterable], progress: bool = False) -> pd.DataFrame:
    """One row per image: `relpath` plus the fifteen coordinates. Unreadable files get
    an `error` instead of stopping the run. No absolute paths are written."""
    if isinstance(paths, (str, os.PathLike)):
        paths = [paths]
    files = find_images(*paths)
    rows = []
    for i, (p, rel) in enumerate(files, 1):
        if progress and (i % 200 == 0 or i == len(files)):
            print(f"[{i}/{len(files)}]", flush=True)
        try:
            rows.append({"relpath": rel, **measure(p)})
        except Exception as e:
            rows.append({"relpath": rel, "error": f"{type(e).__name__}: {str(e).replace(str(p), rel)}"})
    return pd.DataFrame(rows)
