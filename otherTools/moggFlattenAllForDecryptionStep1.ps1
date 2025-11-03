param(
    [Parameter(Mandatory=$true)]
    [string]$RootPath,   # The source path (e.g., C:\RockBand\Songs\Source)
    
    [Parameter(Mandatory=$true)]
    [string]$TempPath    # Temporary folder for Nautilus processing
)

# Function to display usage information
function Show-Usage {
    Write-Host "`nUSAGE INSTRUCTIONS: Copy MOGG Files to Temp Folder" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------" -ForegroundColor Cyan
    Write-Host "This script copies all .mogg files from a recursive source path into a flat temporary folder."
    Write-Host "   -RootPath: The root directory of your entire custom song library."
    Write-Host "   -TempPath: The temporary directory where MOGG files will be copied for Nautilus."
    Write-Host "`nExample:" -ForegroundColor Yellow
    Write-Host "  .\copy_mogg_to_temp.ps1 -RootPath 'C:\MyRB3Library\Original_Songs' -TempPath 'C:\RB3DX_Temp_MOGG_Process'`n" -ForegroundColor Yellow
}

# Check if mandatory parameters were bound (i.e., if $RootPath is empty after parameter binding)
if (-not $RootPath) {
    Show-Usage
    exit
}

# Create the temp directory
if (-not (Test-Path -Path $TempPath)) {
    New-Item -Path $TempPath -ItemType Directory | Out-Null
    Write-Host "Created temporary directory: $TempPath" -ForegroundColor Green
}

Write-Host "Copying all MOGG files from $RootPath to $TempPath..."

# Search recursively and copy files
Get-ChildItem -Path $RootPath -Recurse -Filter "*.mogg" | Copy-Item -Destination $TempPath

Write-Host "Copy complete. Total MOGG files copied: $((Get-ChildItem -Path $TempPath).Count)" -ForegroundColor Yellow
