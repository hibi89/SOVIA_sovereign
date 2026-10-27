@echo off
setlocal
set "SOVIA_APP=%~dp0"
set "SOVIA_RESULTS=%~dp0..\SOVIA_P2_DIAGNOSTICS"
where py >nul 2>&1
if errorlevel 1 goto python_fallback
py -3 -I -B "%SOVIA_APP%owner_p2_selfcheck.py" --output-dir "%SOVIA_RESULTS%"
set "SOVIA_EXIT=%errorlevel%"
goto finished
:python_fallback
where python >nul 2>&1
if errorlevel 1 goto missing_python
python -I -B "%SOVIA_APP%owner_p2_selfcheck.py" --output-dir "%SOVIA_RESULTS%"
set "SOVIA_EXIT=%errorlevel%"
goto finished
:missing_python
echo Python 3.11 or newer is required. Install Python from its official source.
echo No network action or installation was performed by SOVIA.
set "SOVIA_EXIT=2"
:finished
echo.
echo SOVIA P2 self-check exit code: %SOVIA_EXIT%
echo Results folder: "%SOVIA_RESULTS%"
echo Automated tests do not replace manual browser, PDF, or security review.
if /i "%SOVIA_NO_PAUSE%"=="1" goto no_pause
pause
:no_pause
exit /b %SOVIA_EXIT%
