# Module 3 - Very Granular Step-by-Step Guide

This guide is written for a beginner using Windows and VS Code.

## Part A - Create the project folder

1. Open File Explorer.
2. Go to the same course folder you used for Module 2.
3. Create a new folder named `CSc8830_Module3`.
4. Inside it, create these folders:
   - `app`
   - `data`
   - `outputs`
   - `report`
   - `src`
   - `tests`
5. Copy the files from this starter project into the matching folders.

## Part B - Open the project in VS Code

1. Open VS Code.
2. Click **File > Open Folder**.
3. Select the `CSc8830_Module3` folder.
4. In the left Explorer panel, make sure you can see `app`, `data`, `outputs`, `report`, `src`, and `tests`.

## Part C - Open PowerShell in the project folder

In VS Code, choose **Terminal > New Terminal**.

Check the current folder:

```powershell
Get-Location
```

It should end with your Module 3 folder.

## Part D - Create a Python virtual environment

Run:

```powershell
python -m venv .venv
```

Then activate it:

```powershell
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the beginning of the terminal line.

## Part E - Install packages

Run:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Do not move on until the installation finishes without an error.

## Part F - Run the command-line experiment

Run:

```powershell
python src\blur_cli.py --input data\sample_image.png --kernel-size 9 --sigma 2.0
```

The program should print very small errors. A correct run will report an MAE on the order of `1e-14` and say:

`Equivalent within 1e-10: True`

The program also creates files inside `outputs`.

## Part G - Run the tests

Run:

```powershell
python -m pytest -q
```

You should see:

`3 passed`

This checks the Gaussian kernel and the spatial/Fourier equivalence on both grayscale and color images.

## Part H - Run the web application

Run:

```powershell
streamlit run app\app.py
```

A local web address will appear, normally:

`http://localhost:8501`

Open that address in your browser.

## Part I - Demonstrate the application

1. Upload `data\sample_image.png`.
2. Leave the Gaussian kernel at `9`.
3. Leave sigma at `2.0`.
4. Show the original image.
5. Show the spatial convolution result.
6. Show the Fourier-domain result.
7. Show the numerical error values.
8. Show that the 8-bit images are identical.
9. Change the kernel size to 5 and then 15 to show that the same equivalence continues to hold.

## Part J - Optional: use your own photograph

You can upload any normal photograph instead of the sample image. The mathematical comparison should still give errors close to floating-point precision.

## Part K - Complete the report

Open `report/report.md`.

Add:
- your name
- your GitHub repository URL
- screenshots from the web application
- a screenshot of the command-line validation if desired

The report already contains the theory and the validated experimental table.

## Part L - Create the GitHub repository

After the local project is working:

```powershell
git init
git branch -M main
git add .
git commit -m "Initial Module 3 project"
```

Create an empty GitHub repository named something like `CSC8830_Module3`.

Then connect and push it using the repository URL GitHub gives you:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/CSC8830_Module3.git
git push -u origin main
```

## Part M - Record the video

Record the browser showing:
1. the web application,
2. the uploaded image,
3. the spatial blur,
4. the Fourier blur,
5. the numerical errors,
6. the fact that the 8-bit outputs are identical.

Explain in plain English that the same Gaussian filter is being implemented two different ways and that the results agree to floating-point precision.

## Part N - Final submission

Submit:
1. the final PDF report,
2. the screen-recording/video,
3. the accessible GitHub repository link inside the PDF.
