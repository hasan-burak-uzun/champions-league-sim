@echo off
rem Publishes the simulator to GitHub Pages. First run sets up the git repo.
cd /d "%~dp0"
if not exist .git (
    git init -b main
    git remote add origin https://github.com/hasan-burak-uzun/champions-league-sim.git
)
git add -A
git diff --cached --quiet && (
    echo No changes to publish.
    pause
    exit /b 0
)
git commit -m "Update simulator %date%"
git push -u origin main
if errorlevel 1 (
    echo Push FAILED. Create the empty repo champions-league-sim on GitHub first.
) else (
    echo Published: https://hasan-burak-uzun.github.io/champions-league-sim/
)
pause
