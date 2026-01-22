@echo off
echo Starting Steam Product Crawler...

:: STEP 1: Activate Environment
call "C:\ProgramData\miniconda3\Scripts\activate.bat" steam-scraper

:: STEP 2: Change Directory
cd /d "%~dp0"

:: STEP 3: Create Output Directory
if not exist output mkdir output

:: STEP 4: Run Spider
echo.
echo Running Product Spider...
echo Output will be saved to output/products_all.jl
echo Logs will be saved to output/products_all.log
echo.
echo Press Ctrl+C to stop the crawler at any time.
echo.

scrapy crawl products -o output/products_all.jl --logfile=output/products_all.log --loglevel=INFO -s JOBDIR=output/products_all_job -s HTTPCACHE_ENABLED=False

pause
