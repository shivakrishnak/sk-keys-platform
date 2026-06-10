$enc = [System.Text.UTF8Encoding]::new($false)
$tierMap = @{
  'tier-1-foundations'              = 'Foundations'
  'tier-2-networking-security'      = 'Networking & Security'
  'tier-3-java'                     = 'Java'
  'tier-4-data'                     = 'Data'
  'tier-5-distributed-architecture' = 'Distributed Architecture'
  'tier-6-infrastructure-devops'    = 'Infrastructure & DevOps'
  'tier-7-frontend'                 = 'Frontend'
  'tier-8-artificial-intelligence'  = 'Artificial Intelligence'
  'tier-9-professional-domain'      = 'Professional Domain'
}
$root = 'C:\Shiva\northstar\technical-mastery'
$catCount = 0
$entryCount = 0
foreach ($tier in $tierMap.Keys) {
  $tierName = $tierMap[$tier]
  $tierPath = Join-Path $root $tier
  if (-not (Test-Path $tierPath)) { continue }
  foreach ($cat in Get-ChildItem -Directory $tierPath) {
    $idxPath = Join-Path $cat.FullName 'index.md'
    if (Test-Path $idxPath) {
      $c = [IO.File]::ReadAllText($idxPath, [Text.Encoding]::UTF8)
      $n = $c -replace 'parent: "Technical Mastery"', "parent: `"$tierName`""
      if ($n -ne $c) {
        [IO.File]::WriteAllText($idxPath, $n, $enc)
        $catCount++
      }
    }
  }
  $entries = Get-ChildItem -Recurse -Filter '*.md' -Path $tierPath |
    Where-Object { $_.Name -ne 'index.md' }
  foreach ($f in $entries) {
    $c = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8)
    $n = $c -replace 'grand_parent: "Technical Mastery"', "grand_parent: `"$tierName`""
    if ($n -ne $c) {
      [IO.File]::WriteAllText($f.FullName, $n, $enc)
      $entryCount++
    }
  }
}
Write-Host "Category index.md updated: $catCount"
Write-Host "Entry files updated:       $entryCount"
