"""
Regenerate tests/golden/v31.json by running the ORIGINAL research extractor
(vtl_core.py, "VTL v3.1") on examples/images, loading each image the way the
published benchmarks did (PIL convert("L")).

    python tools/golden_from_original.py /path/to/vtl_core.py
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = importlib.util.spec_from_file_location("vtl_core_original", sys.argv[1])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = {}
    for p in sorted((ROOT / "examples" / "images").iterdir()):
        if p.suffix.lower() in {".png", ".jpg"}:
            out[p.name] = mod.extract(np.array(Image.open(p).convert("L")))
    (ROOT / "tests" / "golden").mkdir(parents=True, exist_ok=True)
    (ROOT / "tests" / "golden" / "v31.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print(f"wrote {len(out)} readings")


if __name__ == "__main__":
    main()
