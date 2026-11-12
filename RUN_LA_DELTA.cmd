@echo off
setlocal DisableDelayedExpansion
rem V0.14 synthetic-only. Never contacts LA, installs software, or processes real records.
if not "%~1"=="" if /i not "%~1"=="--ci" goto usage
set "ROOT=%~dp0"
set "PREVIOUS=%~dp0..\SOVIA-LA-DELTA-before"
set "CURRENT=%~dp0..\SOVIA-LA-DELTA-after"
if exist "%PREVIOUS%" goto occupied
if exist "%CURRENT%" goto occupied
set "PYTHON="
set "PY_ARGS="
where python >nul 2>nul
if errorlevel 1 goto try_launcher
python -I -B -c "import sys;sys.exit(0 if sys.version_info >= (3,11) else 2)" >nul 2>nul
if errorlevel 1 goto try_launcher
set "PYTHON=python"
goto ready
:try_launcher
where py >nul 2>nul
if errorlevel 1 goto missing
py -3 -I -B -c "import sys;sys.exit(0 if sys.version_info >= (3,11) else 2)" >nul 2>nul
if errorlevel 1 goto missing
set "PYTHON=py"
set "PY_ARGS=-3"
:ready
%PYTHON% %PY_ARGS% -I -B "%ROOT%verify_portable_la_delta.py" --directory "%ROOT%."
if errorlevel 1 goto failure
%PYTHON% %PY_ARGS% -I -B "%ROOT%sovia_la_owner_review.py" --plan "%ROOT%examples\demo_la_plan_review.json" --policy "%ROOT%examples\demo_policy.json" --observations "%ROOT%examples\demo_la_observations.json" --output-dir "%PREVIOUS%" --synthetic-only
if errorlevel 1 goto failure
%PYTHON% %PY_ARGS% -I -B "%ROOT%sovia_la_owner_review.py" --plan "%ROOT%examples\demo_la_plan_review.json" --policy "%ROOT%examples\demo_policy.json" --observations "%ROOT%examples\demo_la_observations_gap.json" --output-dir "%CURRENT%" --synthetic-only
if errorlevel 1 goto failure
%PYTHON% %PY_ARGS% -I -B "%ROOT%sovia_la_review_delta.py" --previous "%PREVIOUS%" --current "%CURRENT%" --synthetic-only
if errorlevel 1 goto failure
echo SOVIA DELTA SYNTHETIC COMPLETE - UNAUDITED AUTHENTICITY, NO SAFETY CLEARANCE
if /i "%~1"=="--ci" exit /b 0
echo The report prints counts only. Neither bundle proves genuine LA events.
pause
exit /b 0
:usage
echo Usage: RUN_LA_DELTA.cmd [--ci]
goto failure
:occupied
echo Output exists. Previous work preserved; new-only output refused.
goto failure
:missing
echo Python 3.11 or newer required. Nothing installed.
goto failure
:failure
if /i "%~1"=="--ci" exit /b 2
pause
exit /b 2
