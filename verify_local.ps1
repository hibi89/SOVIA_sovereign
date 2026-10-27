# Offline SOVIA verification. Default fast. -Full: all regression + portable v0.12.
# Uses only checked-in synthetic fixtures and fresh TEMP logs; no deletion/deploy.
param([switch]$Full)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Id = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ") + "_" + [guid]::NewGuid().ToString("N").Substring(0, 8)
$Logs = Join-Path ([System.IO.Path]::GetTempPath()) ("SOVIA_VERIFY_" + $Id)
[void](New-Item -ItemType Directory -Path $Logs)
$SummaryPath = Join-Path $Logs "summary.json"
$StartLocation = (Get-Location).Path
$Checks = New-Object System.Collections.ArrayList
$Report = [ordered]@{
    scope = "SYNTHETIC_ONLY_NO_CUSTOMER_DATA"
    mode = $(if ($Full) { "full" } else { "quick" })
    git_sha = "UNAVAILABLE"
    python_version = "UNAVAILABLE"
    checks = @()
    status = "FAIL"
    owner_windows_security_qa = "NOT_CHECKED"
    real_la_integration = "NOT_CHECKED"
}
$Failed = $true

function Invoke-Check {
    param([string]$Name, [string[]]$Arguments)
    $LogFile = Join-Path $Logs ($Name + ".log")
    $Watch = [Diagnostics.Stopwatch]::StartNew()
    $ExitValue = 1
    try {
        $CallArgs = @($PythonPrefix) + @($Arguments)
        & $PythonCommand @CallArgs *> $LogFile
        $ExitValue = [int]$LASTEXITCODE
    } catch {
        "LOCAL_PROCESS_INVOCATION_FAILED" | Out-File -LiteralPath $LogFile -Encoding UTF8
    } finally {
        $Watch.Stop()
    }
    $State = if ($ExitValue -eq 0) { "PASS" } else { "FAIL" }
    [void]$Checks.Add([ordered]@{
        name = $Name
        result = $State
        exit_code = $ExitValue
        elapsed_ms = [int]$Watch.ElapsedMilliseconds
        log_file = [IO.Path]::GetFileName($LogFile)
    })
    Write-Host ("{0}: {1}" -f $Name, $State)
    if ($ExitValue -ne 0) { Write-Host ("Log: " + $LogFile) }
    return ($ExitValue -eq 0)
}

try {
    Set-Location -LiteralPath $Root
    if ($null -ne (Get-Command git -ErrorAction SilentlyContinue)) {
        $Head = & git -C $Root rev-parse HEAD 2>$null
        if ($LASTEXITCODE -eq 0 -and $Head -match '^[a-f0-9]{40}$') {
            $Report.git_sha = [string]$Head
        }
    }
    if ($null -ne (Get-Command py -ErrorAction SilentlyContinue)) {
        $PythonCommand = "py"
        $PythonPrefix = @("-3")
    } else {
        if ($null -eq (Get-Command python -ErrorAction SilentlyContinue)) {
            throw "PYTHON_UNAVAILABLE"
        }
        $PythonCommand = "python"
        $PythonPrefix = @()
    }
    $Version = "import sys; print(sys.version.split()[0]); sys.exit(0 if sys.version_info >= (3,11) else 2)"
    if (-not (Invoke-Check "python_version" @("-B", "-c", $Version))) {
        throw "PYTHON_VERSION_CHECK_FAILED"
    }
    $Report.python_version = (Get-Content -LiteralPath (Join-Path $Logs "python_version.log") -Raw).Trim()
    $Syntax = "import ast,pathlib; r=pathlib.Path('.'); f=sorted(r.glob('sovia_*.py'))+sorted((r/'tests').glob('test_*.py')); [ast.parse(p.read_text(encoding='utf-8-sig'),filename=str(p)) for p in f]; print('AST_PASS',len(f))"
    if (-not (Invoke-Check "source_syntax" @("-B", "-c", $Syntax))) {
        throw "SOURCE_SYNTAX_CHECK_FAILED"
    }
    if (-not (Invoke-Check "la_plan_focused" @("-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_sovia_la_plan_preflight.py", "-v"))) {
        throw "LA_FOCUSED_TESTS_FAILED"
    }
    if (-not (Invoke-Check "la_plan_cli" @("-I", "-B", "sovia_la_plan_preflight.py", "--input", "examples/demo_la_plan_review.json", "--policy", "examples/demo_policy.json", "--synthetic-only"))) {
        throw "LA_PLAN_SMOKE_FAILED"
    }
    if ($Full) {
        if (-not (Invoke-Check "full_regression" @("-B", "-m", "unittest", "discover", "-s", "tests", "-v"))) {
            throw "FULL_REGRESSION_FAILED"
        }
        if (-not (Invoke-Check "v012_portable_smoke" @("-B", "portable_smoke_v012.py"))) {
            throw "V012_SMOKE_FAILED"
        }
    } else {
        [void]$Checks.Add([ordered]@{name="full_regression"; result="SKIP"; exit_code=$null; elapsed_ms=0; log_file=$null})
        [void]$Checks.Add([ordered]@{name="v012_portable_smoke"; result="SKIP"; exit_code=$null; elapsed_ms=0; log_file=$null})
    }
    $Report.status = "PASS"
    $Failed = $false
} catch {
    $Report.status = "FAIL"
    # Do not leak paths, commands, or raw program output in the summary.
    $Report.error_code = ([string]$_.Exception.Message -replace '[^A-Z0-9_]', '_')
} finally {
    $Report.checks = @($Checks.ToArray())
    $Report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $SummaryPath -Encoding UTF8
    Set-Location -LiteralPath $StartLocation
    Write-Host ("SOVIA verifier: " + $Report.status + " ; summary: " + $SummaryPath)
    Write-Host "Real source/authorization/physical security and PDF visuals remain NOT_CHECKED."
}
if ($Failed) { exit 1 }
exit 0
