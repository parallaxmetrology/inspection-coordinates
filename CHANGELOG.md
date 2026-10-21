# Changelog

## 0.1.0 — 2026-10-21

First public release. Wraps the research extractor "VTL v3.1" verbatim, with coordinates renamed for inspection engineers.

- `measure`, `measure_raw`, `measure_many`; `inspcoords` CLI
- Golden tests against the original; all published Carinthia (4,579) and MixedWM38 (7,015) features reproduce exactly
- Benchmarks: Carinthia SEM with classical baselines (downloads from Zenodo), MixedWM38 (bring your own copy)
