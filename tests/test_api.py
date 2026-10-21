from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

import inspection_coordinates as ic
from inspection_coordinates.cli import main

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "examples" / "images"


def test_inputs_agree():
    p = IMAGES / "carinthia_edge_chip_1.jpg"
    a = ic.measure(p)
    b = ic.measure(Image.open(p))
    c = ic.measure(np.array(Image.open(p).convert("L")))
    assert a == b == c


def test_physics_sanity_on_line_space_patterns():
    sharp = ic.measure(IMAGES / "synthetic_lines_sharp.png")
    blur = ic.measure(IMAGES / "synthetic_lines_defocus.png")
    noisy = ic.measure(IMAGES / "synthetic_lines_noisy.png")
    # defocus: edges soften, spectrum moves to low frequencies
    assert blur["image_log_slope"] < 0.5 * sharp["image_log_slope"]
    assert blur["spectral_centroid"] < 0.5 * sharp["spectral_centroid"]
    # stochastic noise: edges get rough
    assert noisy["edge_roughness"] > 3 * sharp["edge_roughness"]


def test_measure_many_safe_and_robust(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "x.png").write_bytes((IMAGES / "synthetic_wafer_center.png").read_bytes())
    (tmp_path / "broken.png").write_bytes(b"nope")
    df = ic.measure_many(tmp_path)
    assert sorted(df["relpath"]) == ["a/x.png", "broken.png"]
    assert str(tmp_path) not in df.to_csv()
    assert df.set_index("relpath").loc["broken.png", "error"]


def test_cli(tmp_path, capsys):
    main(["measure", str(IMAGES / "synthetic_wafer_scratch.png")])
    assert "image_log_slope" in capsys.readouterr().out
    main(["measure", str(IMAGES), "-o", str(tmp_path / "c.csv")])
    assert len(pd.read_csv(tmp_path / "c.csv")) == len([p for p in IMAGES.iterdir() if p.suffix in {".png", ".jpg"}])
