@echo off
setlocal DisableDelayedExpansion
rem 0.15 demonstration uses PUBLIC FABRICATED DATA only. Not real LA.
if not "%~1"=="" if /i not "%~1"=="--ci" goto usage
set "ROOT=%~dp0"
set "OUTPUT=%~dp0..\SOVIA-LA-MINIMAL-DEMO"
if exist "%OUTPUT%" goto occupied
set "PYTHON="
set "PY_ARGS="
where python >nul 2>nul
if errorlevel 1 goto launcher
python -I -B -c "import sys;sys.exit(0 if sys.version_info >= (3,11) else 2)" >nul 2>nul
if errorlevel 1 goto launcher
set "PYTHON=python"
goto ready
:launcher
where py >nul 2>nul
if errorlevel 1 goto unavailable
py -3 -I -B -c "import sys;sys.exit(0 if sys.version_info >= (3,11) else 2)" >nul 2>nul
if errorlevel 1 goto unavailable
set "PYTHON=py"
set "PY_ARGS=-3"
:ready
%PYTHON% %PY_ARGS% -I -B "%ROOT%verify_portable_la_minimal.py" --directory "%ROOT%."
if errorlevel 1 goto failed
%PYTHON% %PY_ARGS% -I -B "%ROOT%sovia_la_minimal_demo.py" --output-dir "%OUTPUT%" --synthetic-only
if errorlevel 1 goto failed
echo SOVIA MINIMAL SYNTHETIC DEMO COMPLETE - NOT LA AUTHENTICATED
if /i "%~1"=="--ci" exit /b 0
echo Output: "%OUTPUT%\synthetic-review\review.html"
echo LA first-party integration is a SEPARATE private runtime test, not this demo.
pause
exit /b 0
:usage
echo Usage: RUN_LA_MINIMAL.cmd [--ci]
goto failed
:occupied
echo Existing output preserved. No overwrite.
goto failed
:unavailable
echo Python 3.11+ required. No installer or download was attempted.
goto failed
:failed
if /i "%~1"=="--ci" exit /b 2
pause
exit /b 2
