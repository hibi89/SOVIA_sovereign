@echo off
setlocal DisableDelayedExpansion
rem Offline synthetic-only smoke from a pristine, verified SOVIA v0.12 ZIP.
rem Double-click to launch and open the LOCAL report; --ci skips UI and pause.
rem Never installs software, calls n8n/network APIs or handles real customer data.
if not "%~1"=="" if /i not "%~1"=="--ci" goto usage
set "ROOT=%~dp0"
set "OUTPUT=%~dp0..\SOVIA-v012-synthetic-output"
if exist "%OUTPUT%" goto occupied

rem Python 3.11+ is required. Respect the configured Python on PATH first.
set "PYTHON="
set "PY_ARGS="
where python >nul 2>nul
if errorlevel 1 goto try_launcher
python -I -B -c "import sys;sys.exit(0 if sys.version_info >= (3,11) else 2)" >nul 2>nul
if errorlevel 1 goto try_launcher
set "PYTHON=python"
goto have_python

:try_launcher
where py >nul 2>nul
if errorlevel 1 goto missing_python
py -3 -I -B -c "import sys;sys.exit(0 if sys.version_info >= (3,11) else 2)" >nul 2>nul
if errorlevel 1 goto missing_python
set "PYTHON=py"
set "PY_ARGS=-3"

:have_python
rem Refuse unexpected ZIP members, edits and NTFS junctions before execution.
%PYTHON% %PY_ARGS% -I -B "%ROOT%verify_portable_v012.py" --directory "%ROOT%."
if errorlevel 1 goto invalid_package

rem The MVP refuses existing outputs and keeps all output outside install root.
%PYTHON% %PY_ARGS% -I -B "%ROOT%sovia_mvp_v012.py" --input "%ROOT%examples\demo_five_rules.json" --output-dir "%OUTPUT%" --synthetic-only
if errorlevel 1 goto audit_failed

rem Read-only consistency gate: reject interrupted, mismatched or damaged
rem HTML/JSON/SQLite before opening the report in the local browser.
%PYTHON% %PY_ARGS% -I -B "%ROOT%sovia_mvp_v012.py" --verify-output-dir "%OUTPUT%"
if errorlevel 1 goto audit_failed

echo SOVIA SYNTHETIC DEMO COMPLETE
echo LOCAL REPORT: "%OUTPUT%\report.html"
if /i "%~1"=="--ci" exit /b 0
start "" "%OUTPUT%\report.html"
echo No customer input, network API or commercial release has been validated.
pause
exit /b 0

:usage
echo Usage: RUN_V012_DEMO.cmd [--ci]
goto failed
:occupied
echo Existing SOVIA-v012-synthetic-output was preserved. No overwrite.
goto failed
:missing_python
echo Python 3.11 or newer is required. Nothing was installed.
goto failed
:invalid_package
echo Package integrity verification failed. No audit was run.
goto failed
:audit_failed
echo Synthetic audit failed. Check the printed refusal code.
goto failed
:failed
if /i "%~1"=="--ci" exit /b 2
pause
exit /b 2
