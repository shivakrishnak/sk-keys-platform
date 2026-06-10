$dir = "technical-mastery\tier-7-frontend\NXT-nextjs-metaframeworks"
$files = @(
  "NXT-043 - React Query TanStack Query Integration.md",
  "NXT-044 - Zustand State Management in Next.js.md",
  "NXT-045 - Server-Side Analytics and Tracking.md",
  "NXT-046 - A-B Testing and Feature Flags.md",
  "NXT-047 - Content Management System (CMS) Integration.md",
  "NXT-048 - GraphQL with Next.js (Apollo, URQL).md",
  "NXT-049 - WebSockets and Real-Time Features.md",
  "NXT-050 - PDF Generation and Document Export.md",
  "NXT-051 - Email Sending (React Email, Resend).md",
  "NXT-052 - Next.js Compiler (SWC).md"
)

Write-Host "=== LIQUID_TAG CHECK ==="
foreach ($f in $files) {
  $path = Join-Path $dir $f
  $content = Get-Content $path -Raw
  if ($content -match '\{\{') {
    $lines = Get-Content $path
    for ($i = 0; $i -lt $lines.Count; $i++) {
      if ($lines[$i] -match '\{\{') {
        Write-Host "$f line $($i+1): $($lines[$i])"
      }
    }
  }
}

Write-Host ""
Write-Host "=== QRC BORDER CHECK ==="
foreach ($f in $files) {
  $path = Join-Path $dir $f
  $lines = Get-Content $path
  $inBox = $false
  for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    if ($line -match '^[┌└]') { $inBox = $true }
    if ($inBox -and $line -match '^[│├]' -and $line -notmatch '│\s*$|\┤\s*$|\┘\s*$') {
      Write-Host "$f line $($i+1): [$line]"
    }
    if ($line -match '^[└┘]') { $inBox = $false }
  }
}
Write-Host "=== DONE ==="
