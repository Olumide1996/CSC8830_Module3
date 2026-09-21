import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from blur_equivalence import comparison_metrics, frequency_convolution, gaussian_kernel, spatial_convolution


def test_gaussian_kernel_is_normalized_and_symmetric():
    kernel = gaussian_kernel(9, 2.0)
    assert np.isclose(kernel.sum(), 1.0)
    assert np.allclose(kernel, np.flip(kernel, axis=0))
    assert np.allclose(kernel, np.flip(kernel, axis=1))


def test_spatial_and_frequency_match_on_grayscale():
    rng = np.random.default_rng(123)
    image = rng.uniform(0, 255, size=(64, 80)).astype(np.float64)
    kernel = gaussian_kernel(7, 1.5)
    spatial = spatial_convolution(image, kernel)
    frequency = frequency_convolution(image, kernel)
    metrics = comparison_metrics(spatial, frequency)
    assert metrics["mae"] < 1e-10
    assert metrics["max_abs_error"] < 1e-8


def test_spatial_and_frequency_match_on_color():
    rng = np.random.default_rng(456)
    image = rng.uniform(0, 255, size=(48, 72, 3)).astype(np.float64)
    kernel = gaussian_kernel(5, 1.2)
    spatial = spatial_convolution(image, kernel)
    frequency = frequency_convolution(image, kernel)
    metrics = comparison_metrics(spatial, frequency)
    assert metrics["mae"] < 1e-10
    assert metrics["rmse"] < 1e-8
