setlocal enabledelayedexpansion

set "szamlalo=1"

for %%F in (*.jpg) do (
    set "ujnev=!szamlalo!.jpg"
    ren "%%F" "!ujnev!"
    set /a szamlalo+=1
)

endlocal