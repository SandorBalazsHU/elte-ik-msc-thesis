:: A helyes mappába lépés
d:
cd diplomamunka
cd elte-ik-msc-thesis

:: Python venv aktiválás
call venv\Scripts\activate

:: Jupyter notebook start
jupyter notebook

:: GIT ellenőrzés
git diff --quiet
IF %ERRORLEVEL% EQU 0 (
    echo "No git change."
) ELSE (
    :: Kérjük be a commit üzenetet
    set /p commit_message="New commit message: "

    :: Commitolunk a megadott üzenettel
    git add -A
    git commit -m "%commit_message%"

    :: Pusholás a távoli repóba
    git push

    IF %ERRORLEVEL% EQU 0 (
        echo "Succesfull push!"
    ) ELSE (
        echo "Push error!"
    )
)

:: Python venv deaktiválás
deactivate

:: Prompt nyitva marad
echo.
pause