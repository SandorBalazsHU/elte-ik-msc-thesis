setlocal enabledelayedexpansion

set inputFolder=%~dp0
set outputFolder=%~dp0\jpg
set i_view="C:\Program Files\IrfanView\i_view64.exe" 

if not exist %outputFolder% mkdir %outputFolder%

for %%f in ("%inputFolder%*.nef") do (
    set outputName=!outputFolder!\%%~nxf.jpg
    %i_view% "%%f" /resize_long=224 /aspectratio /jpgq=80 /convert=!outputName!
)

endlocal