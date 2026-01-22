@echo off
echo Converting results to readable formats...

:: STEP 1: Activate Environment (need python)
call "C:\ProgramData\miniconda3\Scripts\activate.bat" steam-scraper

:: STEP 2: Run Conversion Script
python "%~dp0scripts\convert_jl.py" "%~dp0output\products_all.jl"

echo.
echo Conversion finished. Check the 'output' folder.
pause
