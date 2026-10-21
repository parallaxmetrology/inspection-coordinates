# Lineage

`src/inspection_coordinates/_v31.py` is a verbatim copy of the research extractor `vtl_core.py`, released internally as **VTL v3.1, "Visual Topology of Light"**. The same file runs the Carinthia, NIST and baseline studies; the MixedWM38 and WM-811K scripts carried inline copies, which were checked to give identical outputs.

This repository renames the coordinates for inspection engineers (`inspection_coordinates.NAMES` maps old to new) and adds loading, a CLI and benchmarks. No computation changed:

- `tests/test_golden.py` compares the package with the original file on the 15 sample images.
- The package reproduces all 4,579 published Carinthia feature rows and all 7,015 MixedWM38 rows exactly.
- `tools/golden_from_original.py` regenerates the goldens from any copy of the original.

## Why the rename

The "VTL" name and short keys (`r_v`, `rho_r`, `mu`, `sdi`…) were carried over from the Visual Thinking Lens, a different instrument for composition, where the same short names mean other things (void ratio, packing density, cohesion…). Here they describe intensity physics, so they now have their own names.

## Not in this repository

- The process-monitoring layer (drift tiers, NILS×LER diagnostic, explainability readouts). Available for pilots; see the README.
- The trained classifier and hosted demo.
- PTD-Z, a separate structural instrument for SEM degradation.
