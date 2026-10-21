# Inspection Coordinates

**Fifteen physics-grounded structural coordinates for semiconductor inspection images. No training.**

SEM images, wafer maps, aerial images: the same frozen extractor turns each into fifteen named numbers grounded in how the image formed. Where the bright mass sits, how it spreads, how sharp the edges are relative to local intensity (NILS-like), how rough they are (LER-like), how energy splits across spatial frequencies. No learned parameters, no domain retraining, every number explainable to a process engineer.

On public benchmarks, a simple classifier on these 15 numbers matches the best classical descriptors:

| | Inspection Coordinates (15) | best classical descriptor |
|---|---|---|
| **Carinthia SEM**, production defects, 4 classes | **0.934** balanced accuracy | Haralick GLCM (48 features): 0.931 |
| **MixedWM38 wafer maps**, 8 pattern classes | **0.949** | Zernike moments (45): ≈ 0.946 |

Both are reproducible from the public downloads with the scripts in [`benchmarks/`](benchmarks/). Details, caveats and the rare-class story are in [docs/evidence.md](docs/evidence.md).

## Install

```bash
pip install "inspection-coordinates[bench] @ git+https://github.com/parallaxmetrology/inspection-coordinates"
```

## Use

```python
import inspection_coordinates as ic

c = ic.measure("sem_image.png")
c["image_log_slope"], c["edge_roughness"], c["spectral_centroid"]

df = ic.measure_many("images/")          # one row per image, ready for any classifier or SPC chart
```

```bash
inspcoords measure sem_image.png                 # JSON
inspcoords measure images/ -o coordinates.csv    # a folder
python benchmarks/carinthia.py --baselines       # reproduce the SEM comparison
python benchmarks/mixedwm38.py Wafer_Map_Datasets.npz
```

## The coordinates

| group | coordinates |
|---|---|
| placement | `centroid_offset_x`, `centroid_offset_y`, `peak_offset_x` |
| spread | `radial_variance`, `radial_intensity_correlation` |
| intensity | `mean_intensity`, `intensity_entropy` |
| edges | `image_log_slope` (NILS-like), `edge_roughness` (LER-like), `edge_density`, `dominant_orientation` |
| frequency | `spectral_centroid`, `spectral_power_low`, `spectral_power_mid`, `spectral_power_high` |

Exact definitions, ranges, and how the edge metrics relate to NILS and LER: [docs/coordinates.md](docs/coordinates.md).

## Why use 15 numbers instead of a deep model?

- **Explainable:** a shift in `image_log_slope` or `edge_roughness` points at a physical cause (focus, dose, stochastic noise), not a latent vector.
- **No training data required to extract:** useful when defect classes are rare and labels are expensive.
- **Stable across tools and modalities:** the same extractor reads SEM, wafer maps and aerial images.
- **Cheap:** pure NumPy/OpenCV, milliseconds per image, runs anywhere.

It is not a replacement for a trained classifier when you have abundant labels; it's a compact, interpretable layer that works alongside one. Combining it with classical descriptors does better than either alone.

## Process monitoring: pilots

The research behind this repository also includes a **process-monitoring layer** built on the coordinates: two-tier drift detection, a NILS×LER diagnostic that separates defocus-type degradation from stochastic noise, and plain-language readouts of which coordinate moved and why. That layer isn't in this repository.

If you run inspection, metrology or yield analysis and want to test it on your data, a pilot is welcome: **russellgparrish@gmail.com**. A live demo of the coordinates on sample SEM images and wafer maps is linked from [parallaxmetrology.com](https://www.parallaxmetrology.com/semiconductor_pm.html).

## Contribute

- Run the coordinates on **your** inspection data (any modality) and share how they separate your classes, even if they don't.
- Bring a public dataset we haven't tried.
- Spot a definition that's off from how the field uses a term.

See [CONTRIBUTING.md](CONTRIBUTING.md). Discussion: [Discussions](https://github.com/parallaxmetrology/inspection-coordinates/discussions).

## Part of Parallax Metrology

One principle across domains: structure has geometry, and geometry is measurable without knowing what it means. Siblings: [Visual Thinking Lens](https://github.com/parallaxmetrology/visual-thinking-lens) (composition), [Linguistic Kernel](https://github.com/parallaxmetrology/linguistic-kernel) (text). More at [parallaxmetrology.com](https://www.parallaxmetrology.com).

## License and data

Code: [MIT](LICENSE). Docs: [CC BY 4.0](LICENSE-CONTENT). Sample SEM images in `examples/images/carinthia_*` are from the **Carinthia dataset** (Kofler, Strauß, Zernig, Lazaro Garcia, Boxleitner; Zenodo, DOI [10.5281/zenodo.10715190](https://doi.org/10.5281/zenodo.10715190)), CC BY 4.0. MixedWM38 isn't redistributed here.
