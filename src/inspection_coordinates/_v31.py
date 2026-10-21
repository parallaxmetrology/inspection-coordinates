"""
VTL v3 Core — Visual Topology of Light
15-coordinate image descriptor. Physics-grounded, modality-agnostic.
"""
import numpy as np
import cv2

COORD_NAMES = [
    'delta_x', 'delta_y', 'r_v', 'mu', 'sdi',
    'rho_r', 'x_p', 'theta', 'd_s', 'nils', 'ler',
    'edge_density', 'ds_low', 'ds_mid', 'ds_high'
]

COORD_LABELS = {
    'delta_x':      'Centroid X offset',
    'delta_y':      'Centroid Y offset',
    'r_v':          'Radial variance',
    'mu':           'Mean intensity',
    'sdi':          'Spatial dispersion (entropy)',
    'rho_r':        'Radial correlation',
    'x_p':          'Peak X offset',
    'theta':        'Dominant gradient angle',
    'd_s':          'Spectral spread',
    'nils':         'Edge sharpness (NILS)',
    'ler':          'Edge roughness (LER)',
    'edge_density': 'Edge pixel density',
    'ds_low':       'Low-frequency power fraction',
    'ds_mid':       'Mid-frequency power fraction',
    'ds_high':      'High-frequency power fraction',
}

COORD_DESCRIPTIONS = {
    'delta_x':      'Intensity-weighted centroid horizontal offset from image center. Detects asymmetric defect placement.',
    'delta_y':      'Intensity-weighted centroid vertical offset from image center.',
    'r_v':          'Radial variance of intensity mass. High = diffuse/ring defects. Low = center-concentrated.',
    'mu':           'Mean normalized intensity. Encodes defect density and global brightness.',
    'sdi':          'Normalized Shannon entropy of intensity histogram. High = complex texture. Low = uniform regions.',
    'rho_r':        'Pearson correlation between radial distance and intensity. Encodes whether bright regions are central or peripheral.',
    'x_p':          'Horizontal offset of intensity peak from centroid. Detects asymmetric hot spots.',
    'theta':        'Intensity-weighted dominant gradient orientation. Detects oriented features (scratches, lines).',
    'd_s':          'Spectral spread — center of mass of FFT power spectrum. High = fine detail. Low = coarse structure.',
    'nils':         'Normalized Image Log Slope: median(|∇I|/I) at Canny edge pixels. Edge sharpness normalized by local intensity.',
    'ler':          'Line Edge Roughness: std of lateral contour deviation, normalized by image diagonal. Stochastic noise indicator.',
    'edge_density': 'Fraction of pixels classified as edges by Canny detector. High = complex boundary structure.',
    'ds_low':       'Fraction of FFT power in low spatial frequencies (r < max_r/3). Encodes global form energy.',
    'ds_mid':       'Fraction of FFT power in mid spatial frequencies (max_r/3 ≤ r < 2·max_r/3). Encodes feature-scale energy.',
    'ds_high':      'Fraction of FFT power in high spatial frequencies (r ≥ 2·max_r/3). Encodes edge/noise energy.',
}


def extract(img_arr: np.ndarray) -> dict:
    """
    Extract VTL v3.1 coordinates from an image array.
    Accepts H×W or H×W×C uint8 or float arrays.
    Returns dict of 15 named coordinates.
    """
    img = img_arr.astype(np.float64)
    if img.ndim == 3:
        img = img.mean(axis=2)
    H, W = img.shape

    img_n = (img - img.min()) / (img.max() - img.min() + 1e-9)
    total_mass = img_n.sum() + 1e-9
    ys, xs = np.mgrid[0:H, 0:W]

    # Centroid
    cx = (xs * img_n).sum() / total_mass
    cy = (ys * img_n).sum() / total_mass
    delta_x = float((cx - W / 2) / W)
    delta_y = float((cy - H / 2) / H)

    # Radial variance
    r2 = (xs - cx) ** 2 + (ys - cy) ** 2
    r_v = float((r2 * img_n).sum() / (total_mass * (max(W, H) / 2) ** 2))

    # Mean intensity
    mu = float(img_n.mean())

    # Entropy (SDI)
    hist, _ = np.histogram(img_n.ravel(), bins=64, range=(0, 1))
    h = hist / (hist.sum() + 1e-9)
    h = h[h > 0]
    sdi = float(-np.sum(h * np.log2(h)) / np.log2(64))

    # Radial correlation
    rho_r = float(np.corrcoef(np.sqrt(r2).ravel(), img_n.ravel())[0, 1])
    if np.isnan(rho_r):
        rho_r = 0.0

    # Peak offset
    x_p = float((np.argmax(img_n) % W - cx) / W)

    # Dominant gradient angle
    gx = cv2.Sobel(img_n, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(img_n, cv2.CV_64F, 0, 1, ksize=3)
    gmag = np.sqrt(gx ** 2 + gy ** 2)
    gth = np.arctan2(gy, gx)
    w = gmag / (gmag.sum() + 1e-9)
    theta = float(
        np.arctan2((w * np.sin(2 * gth)).sum(), (w * np.cos(2 * gth)).sum()) / (2 * np.pi)
    )

    # Spectral spread + band decomposition
    fft2 = np.fft.fft2(img_n)
    power = np.abs(np.fft.fftshift(fft2)) ** 2
    fy, fx_f = np.mgrid[-H // 2: H // 2, -W // 2: W // 2]
    fr = np.sqrt(fx_f ** 2 + fy ** 2)
    max_fr = np.sqrt((H // 2) ** 2 + (W // 2) ** 2)
    total_power = power.sum() + 1e-9
    d_s = float((fr * power).sum() / (total_power * max_fr))
    ds_low  = float(power[fr <  max_fr / 3].sum() / total_power)
    ds_mid  = float(power[(fr >= max_fr / 3) & (fr < 2 * max_fr / 3)].sum() / total_power)
    ds_high = float(power[fr >= 2 * max_fr / 3].sum() / total_power)

    # NILS + edge density — Canny mask shared across both coordinates
    img_u8 = (img_n * 255).clip(0, 255).astype(np.uint8)
    edges = cv2.Canny(img_u8, 30, 90)
    em = edges.astype(bool)
    edge_density = float(em.sum() / (H * W))
    si = img_n.copy()
    si[si < 1e-6] = 1e-6
    nils = float(np.clip(np.median(gmag[em] / si[em]) if em.sum() > 0 else 0.0, 0, 10))

    # LER
    cnts, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    devs = []
    for cnt in cnts:
        pts = cnt.squeeze()
        if pts.ndim < 2 or len(pts) < 8:
            continue
        win = max(3, len(pts) // 10)
        xc = pts[:, 0].astype(float)
        yc = pts[:, 1].astype(float)
        d = np.sqrt(
            (xc - np.convolve(xc, np.ones(win) / win, 'same')) ** 2
            + (yc - np.convolve(yc, np.ones(win) / win, 'same')) ** 2
        )
        trim = win // 2
        devs.extend(d[trim:-trim].tolist())
    ler = float(np.std(devs) / np.sqrt(H ** 2 + W ** 2)) if len(devs) >= 10 else 0.0

    return dict(
        delta_x=delta_x, delta_y=delta_y, r_v=r_v, mu=mu,
        sdi=sdi, rho_r=rho_r, x_p=x_p, theta=theta,
        d_s=d_s, nils=nils, ler=ler,
        edge_density=edge_density, ds_low=ds_low, ds_mid=ds_mid, ds_high=ds_high
    )


def coords_array(coords: dict) -> np.ndarray:
    """Return coordinates as ordered numpy array matching COORD_NAMES."""
    return np.array([coords[k] for k in COORD_NAMES])
