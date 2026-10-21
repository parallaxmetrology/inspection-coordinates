# Evidence

All results use the same frozen extractor and a simple probe fit on each dataset's labels. The coordinates themselves never see labels.

## Reproduced in this repository

| benchmark | data | protocol | result |
|---|---|---|---|
| **Carinthia SEM** | 4,579 production SEM images, 4 classes (Particle 55, Normal 4,008, Edge-chip 289, Contamination 227) | RBF SVM, 5-fold stratified CV, balanced accuracy | **0.934 ± 0.034** (`benchmarks/carinthia.py`) |
| **MixedWM38 wafer maps** | 7,015 single-defect maps, 8 classes | linear SVM, 5-fold stratified CV, balanced accuracy | **0.949 ± 0.002** (`benchmarks/mixedwm38.py`) |

The package reproduces the published Carinthia features (all 4,579 images) and MixedWM38 features (all 7,015 maps) exactly.

### Against classical descriptors (Carinthia, same protocol)

| features | n | balanced accuracy |
|---|---|---|
| **Inspection Coordinates** | **15** | **0.934 ± 0.034** |
| Haralick GLCM | 48 | 0.931 ± 0.022 |
| PCA on pixels | 11 | 0.906 ± 0.037 |
| Zernike moments | 45 | 0.903 ± 0.028 |
| LBP | 26 | 0.843 ± 0.037 |
| Hu moments | 7 | 0.691 ± 0.040 |
| HOG | 8,100 | 0.688 ± 0.044 |

Fifteen coordinates match the best classical texture descriptor (Haralick, 48 features) within the cross-validation spread. The two are statistically indistinguishable on this data; neither clearly leads. On MixedWM38, Zernike moments reach a similar level (about 0.946 in an earlier run) to the coordinates' 0.949. What the coordinates add is not a decisive win in accuracy but **15 named, physically interpretable numbers** at that level of accuracy, with no training and the same extractor across modalities.

## What to know

- **Rare classes.** Carinthia's Particle class has 55 images against 4,008 normal ones. Recall is high (≈ 0.99) but precision is around 0.55: some normal images get flagged as particles. Expect to tune thresholds for rare defects.
- **Two Carinthia classes are excluded** (8 and 4 images). The dataset has six classes; the benchmark uses four.
- **WM-811K** (9 classes including "none", heavily imbalanced) reaches 0.63–0.75 balanced accuracy in earlier runs: well above chance (0.11), well below MixedWM38. Not reproduced here; its distribution terms are unclear.
- **Same extractor, separate probes.** "Transfer across modalities" means the coordinates are frozen across SEM, wafer maps and simulated aerial images; a classifier is still fit per dataset.
- **Simulation.** Results on simulated aerial images (Hopkins imaging, focus–exposure matrices) are in the research report and are not yet reproduced in this repository. Validation on real aerial-image (AIMS) data is open.
- **Platforms.** Exact on the reference platform (Apple Silicon); OpenCV and FFT rounding can shift the last digits elsewhere (tests allow 1e-6 relative).
