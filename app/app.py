"""
Streamlit web application for CSc 8830 Module 3.

The app demonstrates image blurring in two mathematically equivalent ways:
1. spatial convolution with a Gaussian kernel, and
2. Fourier-domain multiplication of the image FFT by the kernel FFT.

Run from the project root:
    streamlit run app/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from blur_equivalence import (  # noqa: E402
    comparison_metrics,
    frequency_convolution,
    frequency_magnitude,
    gaussian_kernel,
    spatial_convolution,
)


st.set_page_config(page_title="CSc 8830 Module 3", layout="wide")
st.title("CSc 8830 Module 3: Image Blurring")
st.caption("Spatial convolution vs. Fourier-domain multiplication")

st.markdown(
    "Upload an image, choose a Gaussian blur kernel, and compare the result "
    "from direct spatial filtering with the result from FFT multiplication."
)


# ------------------------------------------------------------------
# Saved outputs from the completed validation experiment
# ------------------------------------------------------------------

st.header("Completed validation example")

st.write(
    "The images and metrics below are the saved outputs from the completed "
    "9×9 Gaussian-blur experiment with sigma = 2.0. You can review the "
    "completed result without uploading an image."
)

saved_output_dir = ROOT / "outputs"

saved_input_path = saved_output_dir / "input.png"
saved_spatial_path = saved_output_dir / "spatial_blur.png"
saved_frequency_path = saved_output_dir / "frequency_blur.png"
saved_difference_path = saved_output_dir / "absolute_difference.png"
saved_input_spectrum_path = saved_output_dir / "input_spectrum.png"
saved_frequency_spectrum_path = saved_output_dir / "frequency_blur_spectrum.png"
saved_metrics_path = saved_output_dir / "metrics.json"

saved_col1, saved_col2, saved_col3 = st.columns(3)

with saved_col1:
    st.image(
        str(saved_input_path),
        caption="Saved original image",
        width="stretch",
    )

with saved_col2:
    st.image(
        str(saved_spatial_path),
        caption="Saved spatial-convolution result",
        width="stretch",
    )

with saved_col3:
    st.image(
        str(saved_frequency_path),
        caption="Saved Fourier-domain result",
        width="stretch",
    )

if saved_metrics_path.exists():
    try:
        import json

        saved_metrics = json.loads(saved_metrics_path.read_text(encoding="utf-8"))

        sm1, sm2, sm3 = st.columns(3)
        sm1.metric("Mean absolute error", f"{saved_metrics['mae']:.3e}")
        sm2.metric("RMSE", f"{saved_metrics['rmse']:.3e}")
        sm3.metric(
            "Maximum absolute error",
            f"{saved_metrics['max_abs_error']:.3e}",
        )

        if saved_metrics.get("byte_outputs_equal") is True:
            st.success(
                "The saved 8-bit spatial and Fourier-domain outputs are identical."
            )
        else:
            st.info("The saved outputs differ only by numerical precision.")
    except Exception as exc:
        st.warning(f"Could not read the saved metrics: {exc}")

with st.expander("Saved difference and Fourier-domain outputs"):
    diff_col1, diff_col2 = st.columns(2)

    with diff_col1:
        st.image(
            str(saved_difference_path),
            caption="Saved 8-bit absolute difference",
            width="stretch",
        )

    with diff_col2:
        st.image(
            str(saved_frequency_spectrum_path),
            caption="Saved blurred-image Fourier magnitude",
            width="stretch",
        )

    st.image(
        str(saved_input_spectrum_path),
        caption="Saved original-image Fourier magnitude",
        width="stretch",
    )

with st.expander("Saved Gaussian kernel used in the experiment"):
    saved_kernel = gaussian_kernel(9, 2.0)
    st.dataframe(np.round(saved_kernel, 5), width="stretch")

st.divider()


# ------------------------------------------------------------------
# Manual experiment
# ------------------------------------------------------------------

st.header("Run the experiment yourself")

uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "bmp"])

col1, col2 = st.columns(2)
with col1:
    kernel_size = st.selectbox("Gaussian kernel size", [3, 5, 7, 9, 11, 15, 21], index=3)
with col2:
    sigma = st.slider("Gaussian sigma", min_value=0.5, max_value=6.0, value=2.0, step=0.5)

if uploaded is not None:
    file_bytes = np.frombuffer(uploaded.read(), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        st.error("The uploaded file could not be decoded as an image.")
        st.stop()

    kernel = gaussian_kernel(kernel_size, sigma)
    spatial = spatial_convolution(image, kernel)
    frequency = frequency_convolution(image, kernel)
    metrics = comparison_metrics(spatial, frequency)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    spatial_u8 = np.clip(np.rint(spatial), 0, 255).astype(np.uint8)
    frequency_u8 = np.clip(np.rint(frequency), 0, 255).astype(np.uint8)
    spatial_rgb = cv2.cvtColor(spatial_u8, cv2.COLOR_BGR2RGB)
    frequency_rgb = cv2.cvtColor(frequency_u8, cv2.COLOR_BGR2RGB)
    byte_difference = cv2.absdiff(spatial_u8, frequency_u8)
    byte_max_error = int(byte_difference.max())
    byte_outputs_equal = bool(np.array_equal(spatial_u8, frequency_u8))

    st.subheader("Results")
    a, b, c = st.columns(3)
    with a:
        st.image(image_rgb, caption="Original image", width="stretch")
    with b:
        st.image(spatial_rgb, caption="Spatial convolution", width="stretch")
    with c:
        st.image(frequency_rgb, caption="Fourier-domain equivalent", width="stretch")

    st.subheader("Numerical validation")
    m1, m2, m3 = st.columns(3)
    m1.metric("Mean absolute error", f"{metrics['mae']:.3e}")
    m2.metric("RMSE", f"{metrics['rmse']:.3e}")
    m3.metric("Maximum absolute error", f"{metrics['max_abs_error']:.3e}")

    if metrics["mae"] < 1e-10:
        st.success("The spatial and Fourier-domain results are numerically equivalent to machine precision.")
    else:
        st.warning("The results are close, but the numerical difference is above the chosen tolerance.")

    st.write(f"8-bit output images identical: **{byte_outputs_equal}** (maximum 8-bit difference: **{byte_max_error}**)")
    st.image(byte_difference, caption="8-bit absolute difference (black means no visible difference)", width="stretch")

    s1, s2 = st.columns(2)
    with s1:
        st.image(frequency_magnitude(image), caption="Original image Fourier magnitude", width="stretch")
    with s2:
        st.image(frequency_magnitude(frequency), caption="Blurred image Fourier magnitude", width="stretch")

    st.subheader("Gaussian kernel")
    st.dataframe(np.round(kernel, 5), width="stretch")

else:
    st.info("Upload an image above to run the experiment.")
