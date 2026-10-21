"""
Command line:

    inspcoords measure image.png                 JSON for one image
    inspcoords measure folder/ -o coords.csv     one row per image
    inspcoords measure image.png --raw           research names (delta_x, r_v, nils…)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _cmd_measure(a):
    from .coords import measure, measure_many, measure_raw
    if len(a.paths) == 1 and Path(a.paths[0]).is_file() and not a.out:
        out = (measure_raw if a.raw else measure)(a.paths[0])
        print(json.dumps({"image": Path(a.paths[0]).name, **out}, indent=2))
        return
    df = measure_many(a.paths, progress=a.out is not None)
    if df.empty:
        sys.exit("No images found.")
    if a.out:
        df.to_csv(a.out, index=False)
        print(f"Wrote {len(df)} rows -> {a.out}")
    else:
        df.to_csv(sys.stdout, index=False)


def main(argv=None):
    p = argparse.ArgumentParser(prog="inspcoords", description="Inspection Coordinates — 15 structural coordinates.")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure", help="coordinates for images or folders")
    m.add_argument("paths", nargs="+")
    m.add_argument("-o", "--out", help="write CSV here")
    m.add_argument("--raw", action="store_true", help="research names instead of public names (single image)")
    m.set_defaults(func=_cmd_measure)
    a = p.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
