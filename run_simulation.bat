@echo off
REM Smart Warehouse Automation Platform - Quick Launcher
REM OS PBL Review 1

echo ======================================================================
echo Smart Warehouse Automation Platform - OS CPU Scheduling Simulation
echo ======================================================================
echo.
echo Running Unit Tests...
python -m unittest discover -s tests -p "test_*.py" -v
echo.
echo ======================================================================
echo Running Warehouse Scheduling Demonstrations...
echo ======================================================================
python main.py --demo
pause
