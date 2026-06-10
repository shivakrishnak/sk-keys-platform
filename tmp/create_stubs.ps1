<#
.SYNOPSIS
Creates stub entry files from a keyword CSV definition file.
.PARAMETER KeywordFile
Path to a CSV file with columns: id,title,difficulty,topic_type,tags,depends_on,nav_order,permalink_slug
.PARAMETER Category
Full category name (e.g. "Caching")
.PARAMETER Tier
Tier folder name (e.g. "tier-4-data")
.PARAMETER Folder
Category folder name (e.g. "CCH-caching")
#>
param(
    [Parameter(Mandatory)][string]$KeywordFile,
    [Parameter(Mandatory)][string]$Category,
    [Parameter(Mandatory)][string]$Tier,
    [Parameter(Mandatory)][string]$Folder
)

$utf8 = [System.Text.UTF8Encoding]::new($false)
$basePath = "c:\Shiva\northstar\technical-mastery\$Tier\$Folder"

$keywords = Import-Csv $KeywordFile

foreach ($kw in $keywords) {
    $fileName = "$($kw.id) - $($kw.title).md"
    $filePath = Join-Path $basePath $fileName

    if (Test-Path $filePath) {
        Write-Host "SKIP (exists): $fileName"
        continue
    }

    $tags = ($kw.tags -split '\|') | ForEach-Object { "  - $_" }
    $tagsBlock = $tags -join "`n"

    $content = @"
---
id: $($kw.id)
title: "$($kw.title)"
category: $Category
tier: $Tier
folder: $Folder
difficulty: $($kw.difficulty)
depends_on: $($kw.depends_on)
used_by:
related:
tags:
$tagsBlock
status: draft
version: 0
schema_version: "entry_v6"
topic_type: $($kw.topic_type)
layout: default
parent: "$Category"
grand_parent: "Technical Mastery"
nav_order: $($kw.nav_order)
permalink: /technical-mastery/$($kw.permalink_slug)/
---

# $($kw.id) - $($kw.title)

> Entry stub. Generate full content using Master Prompt v6.0.
"@

    [System.IO.File]::WriteAllText($filePath, $content, $utf8)
    Write-Host "CREATED: $fileName"
}

Write-Host "`nDone. Created stubs in $basePath"
