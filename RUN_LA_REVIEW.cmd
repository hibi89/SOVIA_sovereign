@echo off
setlocal DisableDelayedExpansion
rem Only synthetic metadata. No live Lightning Azent, API, customer logs or installation.
if not "%~1"=="" if /i not "%~1"=="--ci" goto usage
set "ROOT=%~dp0"
set "OUTPUT=%~dp0..\SOVIA-LA-synthetic-review"
if exist "%OUTPUT%" goto occupied
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
rem Check every extracted source file before running any code from the package.
%PYTHON% %PY_ARGS% -I -B "%ROOT%verify_portable_la_review.py" --directory "%ROOT%."
if errorlevel 1 goto invalid_package
%PYTHON% %PY_ARGS% -I -B "%ROOT%sovia_la_owner_review.py" --plan "%ROOT%examples\demo_la_plan_review.json" --policy "%ROOT%examples\demo_policy.json" --observations "%ROOT%examples\demo_la_observations.json" --output-dir "%OUTPUT%" --synthetic-only
if errorlevel 1 goto audit_failed
%PYTHON% %PY_ARGS% -I -B "%ROOT%sovia_la_owner_review.py" --verify-output-dir "%OUTPUT%"
if errorlevel 1 goto audit_failed
echo SOVIA LA SYNTHETIC REVIEW COMPLETE - NOT AUTHENTICATED
echo LOCAL REPORT: "%OUTPUT%\review.html"
if /i "%~1"=="--ci" exit /b 0
start "" "%OUTPUT%\review.html"
echo No real LA runtime, customer data, genuine approval or release was tested.
pause
exit /b 0
:usage
echo Usage: RUN_LA_REVIEW.cmd [--ci]
goto failed
:occupied
echo Existing output preserved. No overwrite.
goto failed
:missing_python
echo Python 3.11 or newer required. Nothing installed.
goto failed
:invalid_package
echo Package has missing, altered or extra files. Review not started.
goto failed
:audit_failed
echo Synthetic review failed or output was incomplete.
goto failed
:failed
if /i "%~1"=="--ci" exit /b 2
pause
exit /b 2
