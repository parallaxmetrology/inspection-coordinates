"""
Carinthia SEM benchmark: defect classification from the 15 coordinates, against
classical texture and shape descriptors, with the protocol of the published study.

Data: Carinthia dataset (Kofler, Strauß, Zernig, Lazaro Garcia, Boxleitner),
Zenodo DOI 10.5281/zenodo.10715190, CC BY 4.0. Downloaded on first run (~134 MB).

Protocol: classes 1, 3, 4, 6 (Particle, Normal, Edge-chip, Contamination; classes
2 and 5 have 8 and 4 images, too few to cross-validate); RBF SVM (C=10,
class_weight="balanced"); standardized features; 5-fold stratified CV
(shuffle, seed 42); balanced accuracy.

    pip install "inspection-coordinates[bench]"
    python benchmarks/carinthia.py                 # coordinates only (~2 min)
    python benchmarks/carinthia.py --baselines     # plus Haralick, HOG, LBP, Hu, Zernike, PCA-11 (slower)
"""
import argparse
import io
import json
import time
import urllib.request
import zipfile
from math import factorial
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

import inspection_coordinates as ic

URL = "https://zenodo.org/api/records/10715190/files/data.zip/content"
KEEP = {1: "Particle", 3: "Normal", 4: "Edge-chip", 6: "Contamination"}


def fetch(root: Path) -> Path:
    data = root / "data"
    if not (data / "carinthia.csv").exists():
        print("Downloading Carinthia (134 MB) from Zenodo…", flush=True)
        with urllib.request.urlopen(URL) as r:
            zipfile.ZipFile(io.BytesIO(r.read())).extractall(root)
    return data


# ── classical baselines (as in the published comparison) ────────────────────
def haralick(img):
    from skimage.feature import graycomatrix, graycoprops
    f = []
    for d in (1, 3):
        g = graycomatrix(img, distances=[d], angles=[0, np.pi / 4, np.pi / 2, 3 * np.pi / 4],
                         levels=256, symmetric=True, normed=True)
        for prop in ("contrast", "dissimilarity", "homogeneity", "energy", "correlation", "ASM"):
            f.extend(graycoprops(g, prop).flatten().tolist())
    return np.array(f)


def hog_feat(img):
    from skimage.feature import hog
    return hog(cv2.resize(img, (128, 128)), orientations=9, pixels_per_cell=(8, 8),
               cells_per_block=(2, 2), feature_vector=True)


def lbp(img):
    from skimage.feature import local_binary_pattern
    code = local_binary_pattern(cv2.resize(img, (128, 128)), P=24, R=3, method="uniform")
    return np.histogram(code.ravel(), bins=26, range=(0, 26), density=True)[0]


def hu(img):
    from skimage.measure import moments_hu
    m = moments_hu(img.astype(float) / 255.0)
    return -np.sign(m) * np.log10(np.abs(m) + 1e-10)


def zernike(img, radius=64, degree=8):
    r_img = cv2.resize(img, (2 * radius, 2 * radius)).astype(float) / 255.0
    h, w = r_img.shape
    yy, xx = np.mgrid[0:h, 0:w]
    rho = np.sqrt(((yy - h / 2) / radius) ** 2 + ((xx - w / 2) / radius) ** 2)
    th = np.arctan2(yy - h / 2, xx - w / 2)
    mask = rho <= 1.0
    out = []
    for n in range(degree + 1):
        for m in range(-n, n + 1):
            if (n - abs(m)) % 2:
                continue
            R = sum(((-1) ** s * factorial(n - s)
                     / (factorial(s) * factorial((n + abs(m)) // 2 - s) * factorial((n - abs(m)) // 2 - s)))
                    * rho ** (n - 2 * s) for s in range((n - abs(m)) // 2 + 1))
            Z = R * (np.cos(m * th) if m >= 0 else np.sin(-m * th))
            out.append(np.abs(np.sum(r_img * Z * mask) * (n + 1) / np.pi))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("benchmarks/_carinthia"))
    ap.add_argument("--baselines", action="store_true")
    a = ap.parse_args()
    data = fetch(a.root)
    meta = pd.read_csv(data / "carinthia.csv", sep=";")
    meta = meta[meta["label"].isin(KEEP)].reset_index(drop=True)
    y = meta["label"].to_numpy()
    counts = meta["label"].value_counts().sort_index()
    print(f"{len(meta)} images: " + ", ".join(f"{KEEP[k]} {v}" for k, v in counts.items()))

    cache = a.root / "coordinates.csv"
    if cache.exists():
        coords = pd.read_csv(cache)
    else:
        t = time.time()
        coords = pd.DataFrame([ic.measure(data / "images" / f) for f in meta["file_name"]])
        coords.to_csv(cache, index=False)
        print(f"measured coordinates in {time.time() - t:.0f}s")

    banks = {"Inspection Coordinates (15)": coords[list(ic.COORDINATES)].to_numpy()}
    if a.baselines:
        fns = {"Haralick GLCM": haralick, "HOG": hog_feat, "LBP": lbp, "Hu moments": hu, "Zernike": zernike}
        feats = {k: [] for k in fns}
        pixels = []
        t = time.time()
        for f in meta["file_name"]:
            img = np.array(Image.open(data / "images" / f).convert("L"))
            for k, fn in fns.items():
                feats[k].append(fn(img))
            pixels.append(cv2.resize(img, (64, 64)).ravel().astype(float))
        print(f"baseline features in {time.time() - t:.0f}s")
        banks.update({k: np.array(v) for k, v in feats.items()})
        banks["PCA-11 (pixels)"] = np.array(pixels)

    clf = SVC(kernel="rbf", C=10, gamma="scale", class_weight="balanced", random_state=42)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    for name, X in banks.items():
        steps = [("scale", StandardScaler())]
        if name.startswith("PCA"):
            steps.append(("pca", PCA(n_components=11, random_state=42)))
        s = cross_val_score(Pipeline(steps + [("clf", clf)]), X, y, cv=cv, scoring="balanced_accuracy")
        results[name] = {"balanced_accuracy": round(float(s.mean()), 4), "std": round(float(s.std()), 4),
                         "n_features": int(X.shape[1])}
        print(f"{name:30s} {s.mean():.4f} ± {s.std():.4f}  ({X.shape[1]} features)")
    (a.root / "results.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
