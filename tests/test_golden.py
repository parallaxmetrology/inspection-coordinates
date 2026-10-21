"""
The package must reproduce the original research extractor (VTL v3.1) exactly
on the reference platform. tests/golden/v31.json comes from the original file
(tools/golden_from_original.py). OpenCV (Sobel, Canny, contours) and FFT
rounding can differ across CPU architectures, so other platforms get a small
measured tolerance.
"""
import json
import math
import platform
from pathlib import Path

import pytest

import inspection_coordinates as ic

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / "tests" / "golden" / "v31.json").read_text())
REFERENCE = platform.system() == "Darwin" and platform.machine() == "arm64"
REL, ABS = (1e-9, 1e-12) if REFERENCE else (1e-6, 1e-9)


@pytest.mark.parametrize("name", sorted(GOLDEN))
def test_matches_original(name):
    path = ROOT / "examples" / "images" / name
    got = ic.measure_raw(path)
    weak = ic.orientation_strength(path) < 1e-3  # orientation undefined: angle is numerical noise
    for k, v in GOLDEN[name].items():
        if k == "theta" and weak and not REFERENCE:
            continue
        assert math.isclose(got[k], v, rel_tol=REL, abs_tol=ABS), f"{name}: {k} {got[k]} != {v}"


def test_public_names_are_a_renaming():
    p = ROOT / "examples" / "images" / "carinthia_normal_1.jpg"
    raw, pub = ic.measure_raw(p), ic.measure(p)
    assert len(pub) == 15
    for research, public in ic.NAMES.items():
        assert pub[public] == raw[research]
