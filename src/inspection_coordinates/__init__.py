"""
Inspection Coordinates — fifteen physics-grounded structural coordinates for
semiconductor inspection images (SEM, wafer maps, aerial images). No training.

    import inspection_coordinates as ic
    c = ic.measure("sem_image.png")          # dict of 15 coordinates
    df = ic.measure_many("images/")          # one row per image

Part of Parallax Metrology: https://www.parallaxmetrology.com
"""
from .coords import COORDINATES, NAMES, VERSION, measure, measure_many, measure_raw, orientation_strength

__version__ = "0.1.0"
__all__ = ["measure", "measure_many", "measure_raw", "orientation_strength",
           "COORDINATES", "NAMES", "VERSION", "__version__"]
