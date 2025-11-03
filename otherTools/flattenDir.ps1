# flatten-directory.ps1
# Moves all files from subdirectories to the current directory

$currentDir = Get-Location
$movedCount = 0
$conflictCount = 0

# Get all files in subdirectories (not in current directory)
# Use -LiteralPath to handle square brackets and other special characters
$allFiles = Get-ChildItem -LiteralPath $currentDir -Recurse -File
$files = $allFiles | Where-Object { $_.DirectoryName -ne $currentDir.Path }

foreach ($file in $files) {
    # Use -LiteralPath for the source file to handle special characters
    $sourceLiteral = $file.FullName
    $destination = Join-Path $currentDir $file.Name
    
    # Handle filename conflicts
    if (Test-Path -LiteralPath $destination) {
        $conflictCount++
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
        $extension = [System.IO.Path]::GetExtension($file.Name)
        $parentFolder = Split-Path (Split-Path $file.DirectoryName -Parent) -Leaf
        $counter = 1
        
        do {
            $newName = "$baseName`_$parentFolder`_$counter$extension"
            $destination = Join-Path $currentDir $newName
            $counter++
        } while (Test-Path -LiteralPath $destination)
    }
    
    # Use -LiteralPath when moving files
    Move-Item -LiteralPath $sourceLiteral -Destination $destination -Force
    Write-Host "Moved: $($file.Name) -> $(Split-Path $destination -Leaf)"
    $movedCount++
}

# Remove empty directories (using -LiteralPath here too)
Get-ChildItem -LiteralPath $currentDir -Directory -Recurse | 
    Sort-Object { $_.FullName.Length } -Descending | 
    Where-Object { (Get-ChildItem -LiteralPath $_.FullName -Force | Measure-Object).Count -eq 0 } | 
    Remove-Item -Force

Write-Host "`nCompleted: $movedCount files moved, $conflictCount conflicts resolved"
