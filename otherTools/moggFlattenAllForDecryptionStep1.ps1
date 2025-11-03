param(
    [Parameter(Mandatory=$true)]
    [string]$RootPath,   # The source path (e.g., C:\RockBand\Songs\Source)
    
    [Parameter(Mandatory=$true)]
    [string]$TempPath,    # Temporary folder for Nautilus processing

    [Parameter(Mandatory=$false)]
    [string]$LogFile = "",  # Optional log file path for detailed logging

    [Parameter(Mandatory=$false)]
    [switch]$FilterEncryptedOnly = $false  # Optional: Only copy encrypted MOGG files (first two bytes = '11' hex)
)

function Show-Usage {
    Write-Host "`nUSAGE INSTRUCTIONS: Copy MOGG Files to Temp Folder" -ForegroundColor Cyan
    Write-Host "------------------------------------------------" -ForegroundColor Cyan
    Write-Host "This script copies all .mogg files from a recursive source path into a flat temporary folder."
    Write-Host "By default, all MOGG files are copied. Use -FilterEncryptedOnly to copy only encrypted MOGGs."
    Write-Host "   -RootPath: The root directory of your entire custom song library."
    Write-Host "   -TempPath: The temporary directory where MOGG files will be copied for Nautilus."
    Write-Host "   -LogFile: (Optional) Path to a log file for detailed processing information."
    Write-Host "   -FilterEncryptedOnly: (Optional) Only copy encrypted MOGGs (first two bytes = '11' hex)."
    Write-Host "`nExamples:" -ForegroundColor Yellow
    Write-Host "  # Copy all MOGG files (default behavior):" -ForegroundColor Yellow
    Write-Host "  .\moggFlattenAllForDecryptionStep1.ps1 -RootPath 'C:\MyRB3Library\Original_Songs' -TempPath 'C:\RB3DX_Temp_MOGG_Process'" -ForegroundColor Yellow
    Write-Host "`n  # Copy only encrypted MOGG files:" -ForegroundColor Yellow
    Write-Host "  .\moggFlattenAllForDecryptionStep1.ps1 -RootPath 'C:\MyRB3Library\Original_Songs' -TempPath 'C:\RB3DX_Temp_MOGG_Process' -FilterEncryptedOnly -LogFile 'C:\RB3DX_Temp_MOGG_Process\log.txt'`n" -ForegroundColor Yellow
}

# Check if mandatory parameters were bound (i.e., if $RootPath is empty after parameter binding)
if (-not $RootPath) {
    Show-Usage
    exit
}

# Function to check if a MOGG file is encrypted
function Test-MoggEncrypted {
    param([string]$FilePath)
    
    try {
        # Read the first 2 bytes of the file
        $bytes = Get-Content -Path $FilePath -Encoding Byte -TotalCount 2 -ErrorAction Stop
        if ($bytes.Count -ge 2) {
            # Encrypted MOGGs have first two bytes as 0x11 0x11
            # Unencrypted MOGGs have first two bytes as 0x0A 0x0A
            return ($bytes[0] -eq 0x11) -and ($bytes[1] -eq 0x11)
        }
    }
    catch {
        Write-Warning "Could not read file: $FilePath"
    }
    return $false
}


# Create the temp directory
if (-not (Test-Path -Path $TempPath)) {
    New-Item -Path $TempPath -ItemType Directory | Out-Null
    Write-Host "Created temporary directory: $TempPath" -ForegroundColor Green
}

Write-Host "Scanning and copying encrypted MOGG files from $RootPath to $TempPath..."

# Search recursively, check each file, and only copy encrypted ones
$moggFiles = Get-ChildItem -Path $RootPath -Recurse -Filter "*.mogg"
$encryptedCount = 0
$totalCount = 0

foreach ($file in $moggFiles) {
    $totalCount++
    
    # Check if we should filter for encrypted files only
    $shouldCopy = $true
    if ($FilterEncryptedOnly) {
        $shouldCopy = Test-MoggEncrypted -FilePath $file.FullName
    }
    
    if ($shouldCopy) {
        # Get file details for logging
        $fileSize = [math]::Round($file.Length / 1MB, 2)  # Size in MB
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $relativePath = $file.FullName.Replace($RootPath, "").TrimStart("\")

        # Log to console
        if ($FilterEncryptedOnly) {
            Write-Host "Found encrypted MOGG: $($file.Name) ($fileSize MB) - $relativePath" -ForegroundColor Green
        } else {
            Write-Host "Copying: $($file.Name) ($fileSize MB) - $relativePath" -ForegroundColor Green
        }
        
        # Log to file if specified
        if ($LogFile) {
            if ($FilterEncryptedOnly) {
                "$timestamp | ENCRYPTED | $($file.Name) | $fileSize MB | $relativePath | $($file.FullName)" | Out-File -FilePath $LogFile -Append -Encoding UTF8
            } else {
                "$timestamp | COPYING | $($file.Name) | $fileSize MB | $relativePath | $($file.FullName)" | Out-File -FilePath $LogFile -Append -Encoding UTF8
            }
        }
        
        # Copy the file
        Copy-Item -Path $file.FullName -Destination $TempPath
        
        # Log successful copy
        if ($LogFile) {
            "$timestamp | COPIED | $($file.Name) | $fileSize MB | $relativePath" | Out-File -FilePath $LogFile -Append -Encoding UTF8
        }
        
        $encryptedCount++
    }
}

if ($FilterEncryptedOnly) {
    Write-Host "Scan complete. Found $totalCount MOGG files, copied $encryptedCount encrypted files." -ForegroundColor Yellow
} else {
    Write-Host "Copy complete. Found and copied $totalCount MOGG files." -ForegroundColor Yellow
}
