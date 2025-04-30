@echo off
setlocal enabledelayedexpansion

:: -------------------- Settings --------------------
set "iview=C:\Program Files\IrfanView\i_view64.exe"
set "magick=magick"
set "inputFolder=%~dp0"
set "outputFolder=%inputFolder%resized"

:: -------------------- Create output folder --------------------
if not exist "%outputFolder%" (
    echo [INFO] Creating 'resized' folder...
    mkdir "%outputFolder%"
)

:: -------------------- Count input files --------------------
echo.
echo [STEP 1] Counting input files...

set /a count=0
for %%f in ("%inputFolder%*.nef") do set /a count+=1
for %%f in ("%inputFolder%*.jpg") do set /a count+=1

echo Found !count! images to process.

:: -------------------- Resize in parallel --------------------
echo.
echo [STEP 2] Converting all to resized JPG (short side = 224 px)...

set /a i=0
for %%f in ("%inputFolder%*.nef") do (
    set /a i+=1
    start /b "" "%iview%" "%%f" /resize_short=224 /aspectratio /resample /jpgq=80 /convert="%outputFolder%\%%~nf_nef.jpg"
    call :progress !i! !count! "Converting"
)

for %%f in ("%inputFolder%*.jpg") do (
    set /a i+=1
    start /b "" "%iview%" "%%f" /resize_short=224 /aspectratio /resample /jpgq=80 /convert="%outputFolder%\%%~nf_jpg.jpg"
    call :progress !i! !count! "Converting"
)

echo.
echo Waiting for all IrfanView conversions to finish...
call :wait_irfan

:: -------------------- Crop in parallel --------------------
echo.
echo [STEP 3] Cropping to center 224x224 (parallel)...

set /a totalCrop=0
for %%f in ("%outputFolder%\*.jpg") do (
    set /a totalCrop+=1
)

set /a i=0
for %%f in ("%outputFolder%\*.jpg") do (
    set /a i+=1
    start /b "" cmd /c %magick% "%%f" -gravity center -crop 224x224+0+0 +repage "%%f"
    call :progress !i! !totalCrop! "Cropping"
)

echo.
echo Waiting for all cropping to finish...
call :wait_magick

echo.
echo [DONE] All images processed to 224x224 JPG in 'resized' folder.
endlocal
pause
exit /b

:: -------------------- Progress display --------------------
:progress
setlocal
set "current=%~1"
set "total=%~2"
set "label=%~3"
set /a percent=(current*100)/total
echo [%label%] !percent!%% (!current! / !total!)
endlocal
exit /b

:: -------------------- Wait for IrfanView jobs to finish --------------------
:wait_irfan
tasklist | find /I "i_view64.exe" >nul
if not errorlevel 1 (
    timeout /t 1 >nul
    goto wait_irfan
)
exit /b

:: -------------------- Wait for ImageMagick jobs to finish --------------------
:wait_magick
tasklist | find /I "magick.exe" >nul
if not errorlevel 1 (
    timeout /t 1 >nul
    goto wait_magick
)
exit /b
