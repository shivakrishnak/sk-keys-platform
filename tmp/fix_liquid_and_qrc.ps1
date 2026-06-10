#!/usr/bin/env pwsh
#Requires -Version 7
<#
.SYNOPSIS
    Bulk auto-fix: LIQUID_TAG errors and QRC_BORDER_BROKEN errors.

.DESCRIPTION
    Pass 1 - LIQUID_TAG:
      Scans every .md file under technical-mastery/ for code fences that
      contain {{ not already inside a {% raw %}/{% endraw %} block.
      Inserts {% raw %} before the opening ``` and {% endraw %} after
      the closing ```.
      For {{ appearing in PROSE (outside a code fence), wraps each
      {{ pattern }} occurrence with inline {% raw %}{{ }}{% endraw %}.

    Pass 2 - QRC_BORDER_BROKEN:
      Fixes box-drawing border lines with wrong trailing characters:
        ├...─ │  ->  ├...─┤
        └...─ │  ->  └...─┘
        │ content (no ending │)  ->  │ content │

    All output files are UTF-8 without BOM.
#>
param(
    [string]$RootPath = "c:\Shiva\northstar\technical-mastery",
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$enc = [System.Text.UTF8Encoding]::new($false)

$allFiles = Get-ChildItem -Path $RootPath -Filter "*.md" -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch [regex]::Escape('\_config\') }

$fixedFiles  = [System.Collections.Generic.List[string]]::new()
$errorFiles  = [System.Collections.Generic.List[string]]::new()
$totalLiquid = 0
$totalQRC    = 0

foreach ($file in $allFiles) {
    try {
        $lines    = [System.IO.File]::ReadAllLines($file.FullName, $enc)
        $modified = $false

        # ────────────────────────────────────────────────────────────────
        # PASS 1a: Find code fences containing {{ outside {% raw %} blocks
        # ────────────────────────────────────────────────────────────────
        $fencesNeedingWrap = [System.Collections.Generic.List[hashtable]]::new()
        $inRaw    = $false
        $inFence  = $false
        $fStart   = -1
        $fLiquid  = $false

        for ($i = 0; $i -lt $lines.Length; $i++) {
            $line    = $lines[$i]
            $trimmed = $line.Trim()

            # Track raw boundaries (exact match to avoid false positives)
            if ($trimmed -eq '{% raw %}')    { $inRaw = $true;  continue }
            if ($trimmed -eq '{% endraw %}') { $inRaw = $false; continue }

            if (-not $inRaw) {
                if ($trimmed -match '^```') {
                    if (-not $inFence) {
                        $inFence = $true
                        $fStart  = $i
                        $fLiquid = $false
                    } else {
                        if ($fLiquid) {
                            $fencesNeedingWrap.Add(@{ Start = $fStart; End = $i })
                        }
                        $inFence = $false
                        $fStart  = -1
                        $fLiquid = $false
                    }
                } elseif ($inFence -and $line -match '\{\{') {
                    $fLiquid = $true
                } elseif (-not $inFence -and $line -match '\{\{') {
                    # {{ in PROSE: wrap each {{ pattern }} occurrence inline
                    $newLine = [regex]::Replace($line, '\{\{(.*?)\}\}',
                                               '{% raw %}{{$1}}{% endraw %}')
                    if ($newLine -ne $line) {
                        $lines[$i] = $newLine
                        $modified  = $true
                        $totalLiquid++
                    }
                }
            }
        }

        # ────────────────────────────────────────────────────────────────
        # PASS 1b: Insert {% raw %}/{% endraw %} around identified fences
        # ────────────────────────────────────────────────────────────────
        if ($fencesNeedingWrap.Count -gt 0) {
            $insertBefore = @{}
            $insertAfter  = @{}

            foreach ($fence in $fencesNeedingWrap) {
                $insertBefore[$fence.Start] = $true
                $insertAfter[$fence.End]    = $true
            }

            $withRaw = [System.Collections.Generic.List[string]]::new(
                          $lines.Length + $fencesNeedingWrap.Count * 2)

            for ($i = 0; $i -lt $lines.Length; $i++) {
                if ($insertBefore.ContainsKey($i)) { $withRaw.Add('{% raw %}')    }
                $withRaw.Add($lines[$i])
                if ($insertAfter.ContainsKey($i))  { $withRaw.Add('{% endraw %}') }
            }

            $lines        = $withRaw.ToArray()
            $modified     = $true
            $totalLiquid += $fencesNeedingWrap.Count
        }

        # ────────────────────────────────────────────────────────────────
        # PASS 2: Fix QRC_BORDER_BROKEN (box border lines wrong trailing)
        # ────────────────────────────────────────────────────────────────
        $inBox     = $false
        $finalList = [System.Collections.Generic.List[string]]::new($lines.Length)

        foreach ($line in $lines) {
            $trimmed = $line.TrimEnd()
            $out     = $line          # default: emit original line unchanged

            if ($trimmed -match '^┌' -and $trimmed -match '┐$') {
                # Valid top border - enter box mode
                $inBox = $true

            } elseif ($inBox -and $trimmed -match '^└') {
                if ($trimmed -notmatch '┘$') {
                    $out      = ($trimmed -replace '\s*│\s*$', '') + '┘'
                    $modified = $true
                    $totalQRC++
                }
                $inBox = $false

            } elseif ($inBox -and $trimmed -match '^├') {
                if ($trimmed -notmatch '┤$') {
                    $out      = ($trimmed -replace '\s*│\s*$', '') + '┤'
                    $modified = $true
                    $totalQRC++
                }

            } elseif ($inBox -and $trimmed -match '^│' -and
                      $trimmed -ne '' -and $trimmed -notmatch '│$') {
                # Content line missing closing │
                $out      = $trimmed + ' │'
                $modified = $true
                $totalQRC++
            }

            $finalList.Add($out)
        }

        if ($modified) {
            if (-not $DryRun) {
                [System.IO.File]::WriteAllLines($file.FullName, $finalList.ToArray(), $enc)
            }
            $rel = $file.FullName -replace [regex]::Escape('c:\Shiva\northstar\'), ''
            $fixedFiles.Add($rel)
            Write-Host "FIXED: $($file.Name)"
        }
    }
    catch {
        $errorFiles.Add($file.FullName)
        Write-Warning "ERROR processing $($file.Name): $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "======================================"
Write-Host "Files modified  : $($fixedFiles.Count)"
Write-Host "Liquid fixes    : $totalLiquid (fences + prose occurrences)"
Write-Host "QRC fixes       : $totalQRC"
Write-Host "Files with errors: $($errorFiles.Count)"
if ($errorFiles.Count -gt 0) {
    $errorFiles | ForEach-Object { Write-Host "  FAILED: $_" }
}
if ($DryRun) {
    Write-Host ""
    Write-Host "[DRY RUN] No files were written."
}
