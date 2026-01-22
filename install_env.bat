@echo off
echo Setting up Steam Scraper Environment...

:: STEP 1: Activate Base Conda
call "C:\ProgramData\miniconda3\Scripts\activate.bat" base

:: STEP 2: Create Conda Environment
echo.
echo Creating conda environment 'steam-scraper'...
call conda create -n steam-scraper python=3.9 -y

:: STEP 3: Activate the New Environment
echo.
echo Activating 'steam-scraper' environment...
call "C:\ProgramData\miniconda3\Scripts\activate.bat" steam-scraper

:: STEP 4: Install Scrapy via Conda
echo.
echo Installing Scrapy via Conda...
call conda install scrapy itemloaders -y

:: STEP 5: Install Other Dependencies
echo.
echo Installing requirements via pip...
cd /d "%~dp0"
call pip install -r requirements.txt

echo.
echo Setup Complete!
pause
