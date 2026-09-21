"""
Command-line demonstration for Module 3 image blurring.

Example:
    python src/blur_cli.py --input data/sample_image.png --kernel-size 9 --sigma 2.0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2

from blur_equivalence import (
    comparison_metrics,
    frequency_convolution,
    frequency_magnitude,
    gaussian_kernel,
    load_image,
    save_image,
    spatial_convolution,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare spatial and FFT image blurring.")
    parser.add_argument("--input", required=True, help="Input image path")
    parser.add_argument("--kernel-size", type=int, default=9, help="Odd Gaussian kernel size")
    parser.add_argument("--sigma", type=float, default=2.0, help="Gaussian sigma")
    parser.add_argument("--output-dir", default="outputs", help="Directory for results")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image = load_image(args.input)
    kernel = gaussian_kernel(args.kernel_size, args.sigma)

    spatial = spatial_convolution(image, kernel)
    frequency = frequency_convolution(image, kernel)
    metrics = comparison_metrics(spatial, frequency)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    save_image(output_dir / "input.png", image)
    save_image(output_dir / "spatial_blur.png", spatial)
    save_image(output_dir / "frequency_blur.png", frequency)

    difference = cv2.absdiff(
        image.astype("uint8"),
        image.astype("uint8")
    )  # placeholder overwritten below for explicit float comparison visualization
    raw_diff = abs(spatial - frequency)
    if raw_diff.ndim == 3:
        raw_diff = raw_diff.max(axis=2)
    save_image(output_dir / "absolute_difference.png", raw_diff)
    save_image(output_dir / "input_spectrum.png", frequency_magnitude(image))
    save_image(output_dir / "frequency_blur_spectrum.png", frequency_magnitude(frequency))

    payload = {
        "input": str(Path(args.input)),
        "kernel_size": args.kernel_size,
        "sigma": args.sigma,
        **metrics,
    }
    (output_dir / "metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("Module 3 Fourier Equivalence Validation")
    print(f"Input image: {args.input}")
    print(f"Kernel: {args.kernel_size}x{args.kernel_size} Gaussian, sigma={args.sigma}")
    print(f"MAE:            {metrics['mae']:.12e}")
    print(f"RMSE:           {metrics['rmse']:.12e}")
    print(f"Maximum error:  {metrics['max_abs_error']:.12e}")
    print("Equivalent within 1e-10:", metrics["mae"] < 1e-10)


if __name__ == "__main__":
    main()
