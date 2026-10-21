# The fifteen coordinates

Input: a grayscale image (files are converted with PIL `convert("L")`; arrays are used as given, color averaged). The image is min–max normalized to [0, 1], call it *I*, and treated as an intensity mass distribution. No training, no learned parameters, no resizing inside the extractor.

| name | definition | reads | range |
|---|---|---|---|
| `centroid_offset_x` | (intensity-weighted centroid x − W/2) / W | horizontal displacement of bright mass | ≈ −0.5…0.5 |
| `centroid_offset_y` | (centroid y − H/2) / H; + = lower | vertical displacement | ≈ −0.5…0.5 |
| `radial_variance` | Σ I·r² / (Σ I · (max(W,H)/2)²), r from the centroid | diffuse/ring (high) vs concentrated (low) mass | 0…~2 |
| `mean_intensity` | mean of *I* | overall brightness / defect density on wafer maps | 0…1 |
| `intensity_entropy` | Shannon entropy of a 64-bin histogram of *I*, / log₂ 64 | tonal complexity | 0…1 |
| `radial_intensity_correlation` | Pearson r between distance from centroid and *I* | bright periphery (+) vs bright core (−) | −1…1 |
| `peak_offset_x` | (x of the brightest pixel − centroid x) / W | asymmetric hot spots | ≈ −1…1 |
| `dominant_orientation` | gradient-weighted mean of doubled gradient angle, / 2π | dominant edge direction (scratches, lines) | −0.5…0.5 |
| `spectral_centroid` | Σ f·P(f) / (Σ P · f_max), FFT power P, radial frequency f | fine detail (high) vs coarse structure (low) | 0…1 |
| `spectral_power_low` / `_mid` / `_high` | share of FFT power in radial bands [0, ⅓), [⅓, ⅔), [⅔, 1] of f_max | form / feature-scale / edge-and-noise energy | 0…1 each |
| `edge_density` | share of pixels on Canny edges (thresholds 30, 90 on 8-bit *I*) | boundary complexity | 0…1 |
| `image_log_slope` | median of \|∇I\| / I on Canny edge pixels (Sobel 3×3), clipped to 10 | edge sharpness relative to local intensity | 0…10 |
| `edge_roughness` | std of contour points' deviation from a moving-average contour (window = len/10), / image diagonal | stochastic edge roughness | ≥ 0 |

## Relation to lithography metrics

- **`image_log_slope` is NILS-like, not NILS.** NILS is the image log-slope at the feature edge *multiplied by the feature width* (CD). Here it's per pixel and not normalized by CD, so compare it within one magnification and pattern, or multiply by your CD in pixels.
- **`edge_roughness` is LER-like.** It measures contour wobble in pixels relative to the image diagonal, not 3σ LER in nm. It rises with stochastic noise and is useful as a relative indicator.
- In simulation (focus–exposure series), defocus lowers `image_log_slope` and `spectral_centroid`, and stochastic noise raises `edge_roughness`. The tests check these directions on synthetic line-space patterns.

## Research names

The coordinates were developed as "VTL v3.1 (Visual Topology of Light)". `inspection_coordinates.measure_raw` returns the original names (`delta_x`, `r_v`, `rho_r`, `mu`, `sdi`, `x_p`, `theta`, `d_s`, `nils`, `ler`, `edge_density`, `ds_low`, `ds_mid`, `ds_high`), and `inspection_coordinates.NAMES` maps them. These are **not** the coordinates of the Visual Thinking Lens (a separate Parallax Metrology instrument for composition), even where the old short names coincide.
