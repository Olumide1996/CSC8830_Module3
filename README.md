# CSc 8830 Computer Vision - Module 3

## Assignment
**Image blurring using a filtering approach** and experimental validation of the Fourier-domain convolution theorem.

The assignment asks for a working implementation, a web application, a GitHub repository, and a theory/experiment section showing that spatial convolution gives the same result as multiplication in the Fourier domain.

## Project structure

```text
CSc8830_Module3_solution/
├── app/
│   └── app.py
├── data/
│   └── sample_image.png
├── outputs/
├── report/
│   └── report.md
├── src/
│   ├── blur_equivalence.py
│   └── blur_cli.py
├── tests/
│   └── test_blur_equivalence.py
├── .gitignore
└── requirements.txt
```

## Setup (Windows PowerShell)

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the command-line experiment

From the project root:

```powershell
python src\blur_cli.py --input data\sample_image.png --kernel-size 9 --sigma 2.0
```

This produces:
- `outputs/spatial_blur.png`
- `outputs/frequency_blur.png`
- `outputs/absolute_difference.png`
- `outputs/input_spectrum.png`
- `outputs/frequency_blur_spectrum.png`
- `outputs/metrics.json`

## Run the tests

```powershell
python -m pytest -q
```

All tests should pass.

## Run the web application

```powershell
streamlit run app\app.py
```

Then open the local URL shown by Streamlit, normally `http://localhost:8501`.

## What the implementation demonstrates

1. A normalized Gaussian kernel is created in the spatial domain.
2. The image is blurred using centered zero-padded spatial convolution.
3. The same image and kernel are zero-padded for linear convolution.
4. Their 2-D FFTs are multiplied element by element.
5. The inverse FFT returns the Fourier-domain blur result.
6. The two outputs are compared numerically using MAE, RMSE, and maximum absolute error.

## Important theory note

The discrete Fourier transform converts **circular convolution** into multiplication. To match ordinary linear convolution with zero padding, the implementation pads the image and kernel to `(H + Kh - 1) x (W + Kw - 1)` before taking the FFT, then crops the centered result.

## GitHub requirement

Create a GitHub repository for this project and include its URL in the final PDF submission.
