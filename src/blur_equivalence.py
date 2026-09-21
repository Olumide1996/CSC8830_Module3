"""
Module 3 - Image Blurring and Fourier-Domain Equivalence

This module implements Gaussian spatial convolution and its equivalent
frequency-domain implementation using the 2-D FFT.

The implementation uses zero-padding so that the FFT calculation performs
linear convolution rather than circular convolution. The result is then
cropped to the same image size as the spatial result.
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import cv2
import numpy as np


def gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    """Create a normalized 2-D Gaussian kernel."""
    if size < 3 or size % 2 == 0:
        raise ValueError("Kernel size must be an odd integer >= 3.")
    if sigma <= 0:
        raise ValueError("Sigma must be greater than 0.")

    radius = size // 2
    axis = np.arange(-radius, radius + 1, dtype=np.float64)
    xx, yy = np.meshgrid(axis, axis)
    kernel = np.exp(-((xx**2 + yy**2) / (2.0 * sigma**2)))
    kernel /= kernel.sum()
    return kernel


def _as_float64(image: np.ndarray) -> np.ndarray:
    """Return an image as float64 without changing its numeric intensity scale."""
    if image.ndim not in (2, 3):
        raise ValueError("Image must be grayscale (H,W) or color (H,W,C).")
    return image.astype(np.float64, copy=False)


def spatial_convolution(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Apply centered zero-padded spatial convolution."""
    image_f = _as_float64(image)
    kernel = np.asarray(kernel, dtype=np.float64)
    if kernel.ndim != 2:
        raise ValueError("Kernel must be 2-D.")

    # OpenCV filter2D performs correlation. Flipping the kernel converts it to
    # mathematical convolution. Gaussian kernels are symmetric, so the result
    # is unchanged in this particular experiment, but the code is explicit.
    flipped = np.flip(kernel, axis=(0, 1))
    border_type = cv2.BORDER_CONSTANT

    if image_f.ndim == 2:
        return cv2.filter2D(image_f, ddepth=cv2.CV_64F, kernel=flipped, borderType=border_type)

    channels = [
        cv2.filter2D(image_f[:, :, c], ddepth=cv2.CV_64F, kernel=flipped, borderType=border_type)
        for c in range(image_f.shape[2])
    ]
    return np.stack(channels, axis=2)


def frequency_convolution(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Apply the same centered zero-padded convolution using FFT multiplication."""
    image_f = _as_float64(image)
    kernel = np.asarray(kernel, dtype=np.float64)
    if kernel.ndim != 2:
        raise ValueError("Kernel must be 2-D.")

    h, w = image_f.shape[:2]
    kh, kw = kernel.shape

    # These sizes are sufficient for a full linear convolution.
    padded_shape = (h + kh - 1, w + kw - 1)

    kernel_padded = np.zeros(padded_shape, dtype=np.float64)
    kernel_padded[:kh, :kw] = kernel
    kernel_fft = np.fft.fft2(kernel_padded)

    def convolve_channel(channel: np.ndarray) -> np.ndarray:
        image_padded = np.zeros(padded_shape, dtype=np.float64)
        image_padded[:h, :w] = channel
        result_full = np.fft.ifft2(
            np.fft.fft2(image_padded) * kernel_fft
        ).real

        # Crop the centered 'same' result, matching the centered spatial filter.
        top = kh // 2
        left = kw // 2
        return result_full[top : top + h, left : left + w]

    if image_f.ndim == 2:
        return convolve_channel(image_f)

    channels = [convolve_channel(image_f[:, :, c]) for c in range(image_f.shape[2])]
    return np.stack(channels, axis=2)


def comparison_metrics(a: np.ndarray, b: np.ndarray) -> dict:
    """Compute numerical differences between two equally sized arrays."""
    if a.shape != b.shape:
        raise ValueError("Images must have the same shape for comparison.")

    diff = np.abs(a.astype(np.float64) - b.astype(np.float64))
    return {
        "mae": float(np.mean(diff)),
        "rmse": float(np.sqrt(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))),
        "max_abs_error": float(np.max(diff)),
        "mean_abs_diff": float(np.mean(diff)),
    }


def to_uint8(image: np.ndarray) -> np.ndarray:
    """Convert a floating-point image to display/save-friendly uint8."""
    return np.clip(np.rint(image), 0, 255).astype(np.uint8)


def frequency_magnitude(image: np.ndarray) -> np.ndarray:
    """Return a log-scaled, normalized magnitude spectrum for visualization."""
    if image.ndim == 3:
        gray = cv2.cvtColor(to_uint8(image), cv2.COLOR_BGR2GRAY).astype(np.float64)
    else:
        gray = image.astype(np.float64)
    spectrum = np.fft.fftshift(np.fft.fft2(gray))
    magnitude = np.log1p(np.abs(spectrum))
    normalized = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
    return normalized.astype(np.uint8)


def load_image(path: str | Path) -> np.ndarray:
    """Load an image from disk as BGR."""
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return image


def save_image(path: str | Path, image: np.ndarray) -> None:
    """Save an image, raising an error if OpenCV cannot write it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), to_uint8(image)):
        raise OSError(f"Could not write image: {path}")
