# Contributing

Most useful contributions come from people with real inspection data.

- **Results on your data.** Run `inspcoords measure your_images/ -o coords.csv`, fit any simple classifier or SPC chart, and share how the coordinates separate your classes or track your process, including where they don't. You don't need to share images or anything proprietary; summary numbers help.
- **Public datasets.** Point us at open inspection, metrology or wafer-map data we haven't benchmarked.
- **Terminology.** If a coordinate's name or description doesn't match how the field uses a term, open an issue.

## Development

```bash
git clone https://github.com/parallaxmetrology/inspection-coordinates
cd inspection-coordinates
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## The firm rule

`src/inspection_coordinates/_v31.py` is frozen. Results across studies are only comparable if the extractor doesn't change. New coordinates go in new modules, or into a future version with its own name, golden files and changelog. `tests/test_golden.py` must keep passing.

Be kind and specific. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
