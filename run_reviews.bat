@echo off
echo Starting Steam Review Crawler...

:: STEP 1: Activate Environment
call "C:\ProgramData\miniconda3\Scripts\activate.bat" steam-scraper

:: STEP 2: Change Directory
cd /d "%~dp0"

:: STEP 3: Create Output Directory
if not exist output mkdir output

:: STEP 4: Run Spider
echo.
echo Running Review Spider...
echo.

scrapy crawl reviews -o output/reviews.jl -s JOBDIR=output/reviews_job

pause
