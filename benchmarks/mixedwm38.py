"""
MixedWM38 wafer-map benchmark: single-defect classification (8 classes) from the
15 coordinates.

Data: MixedWM38 (Wang et al., "Deformable convolutional networks for efficient
mixed-type wafer defect pattern recognition", IEEE TSM 2020), distributed from
https://github.com/Junliangwangdhu/WaferMap. The repository states no license,
so this script doesn't download it: fetch `Wafer_Map_Datasets.npz` yourself and
pass its path.

Protocol (as published): maps with exactly one defect type; rendered 0→15,
pass→80, fail→240; resized to 64×64 (linear); linear SVM (class_weight
"balanced"); 5-fold stratified CV (shuffle, seed 42); balanced accuracy.
Standardization is fit inside each fold here (the original fit it once on all
data), so expect a result within a few thousandths of the published 0.949.

    python benchmarks/mixedwm38.py /path/to/Wafer_Map_Datasets.npz
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

import inspection_coordinates as ic

DEFECTS = ["Center", "Donut", "Edge-Loc", "Edge-Ring", "Loc", "Near-full", "Random", "Scratch"]


def render(wm: np.ndarray) -> np.ndarray:
    img = np.zeros_like(wm, dtype=np.uint8)
    img[wm == 1] = 80
    img[wm == 2] = 240
    img[wm == 0] = 15
    return cv2.resize(img, (64, 64), interpolation=cv2.INTER_LINEAR).astype(np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("npz", type=Path)
    ap.add_argument("--out", type=Path, default=Path("benchmarks/_mixedwm38"))
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    d = np.load(a.npz, allow_pickle=True)
    maps, onehot = d["arr_0"], d["arr_1"]
    single = onehot.sum(axis=1) == 1
    maps, labels = maps[single], np.array([DEFECTS[int(np.argmax(r))] for r in onehot[single]])
    print(f"{len(maps)} single-defect maps")

    cache = a.out / "coordinates.csv"
    if cache.exists():
        coords = pd.read_csv(cache)
    else:
        coords = pd.DataFrame([ic.measure(render(m)) for m in maps])
        coords.to_csv(cache, index=False)

    pipe = Pipeline([("scale", StandardScaler()),
                     ("clf", LinearSVC(max_iter=5000, class_weight="balanced", random_state=42))])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    s = cross_val_score(pipe, coords[list(ic.COORDINATES)].to_numpy(), labels, cv=cv, scoring="balanced_accuracy")
    res = {"balanced_accuracy": round(float(s.mean()), 4), "std": round(float(s.std()), 4),
           "n_maps": int(len(maps)), "n_classes": len(DEFECTS), "chance": round(1 / len(DEFECTS), 4)}
    print(json.dumps(res, indent=2))
    (a.out / "results.json").write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
