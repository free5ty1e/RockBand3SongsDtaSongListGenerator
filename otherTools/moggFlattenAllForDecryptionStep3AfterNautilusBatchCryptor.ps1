param(
    [Parameter(Mandatory=$true)]
    [string]$RootPath,   # The original song library path (used for structure)
    
    [Parameter(Mandatory=$true)]
    [string]$TempPath,   # Temporary folder (where MOGG files were fixed by Nautilus)

    [Parameter(Mandatory=$true)]
    [string]$OutputPath  # The destination path for the clean, final library
)

# Function to display usage information
function Show-Usage {
    Write-Host "`nUSAGE INSTRUCTIONS: Integrate Fixed MOGGs and Build Library (Checksum Verified)" -ForegroundColor Cyan
    Write-Host "-----------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "This script uses SHA-256 checksums to verify if Nautilus actually changed the MOGG file's content, ensuring ONLY truly fixed songs are copied."
    Write-Host "   -RootPath:  The root directory of your original custom song library (used as the source template)."
    Write-Host "   -TempPath:  The temporary directory where Nautilus decrypted the MOGGs (must contain the 'decrypted' subfolder)."
    Write-Host "   -OutputPath: The final, clean directory to store ONLY the verified fixed songs for the PS3."
    Write-Host "`nExample:" -ForegroundColor Yellow
    Write-Host "  .\integrate_fixed_mogg.ps1 -RootPath 'C:\MyRB3Library\Original_Songs' -TempPath 'C:\RB3DX_Temp_MOGG_Process' -OutputPath 'D:\RB3DX_PS3_Upload\Cleaned_Songs'`n" -ForegroundColor Yellow
}

# Define the function to get the SHA256 hash
function Get-FileHashSHA256 {
    param([string]$Path)
    # The built-in Get-FileHash cmdlet is the most reliable method
    (Get-FileHash -Path $Path -Algorithm SHA256).Hash
}

# Check if mandatory parameters were bound
if (-not $RootPath -or -not $TempPath -or -not $OutputPath) {
    Show-Usage
    exit
}

# --- Main Script Logic Starts Here ---

# Define the source of the fixed files
$FixedMoggSource = Join-Path -Path $TempPath -ChildPath "decrypted"
if (-not (Test-Path -Path $FixedMoggSource)) {
    Write-Host "ERROR: Could not find the required 'decrypted' subfolder in $TempPath" -ForegroundColor Red
    Write-Host "Please ensure Nautilus created the decrypted folder correctly and run the script again." -ForegroundColor Red
    exit 1
}

# Ensure output path exists
if (-not (Test-Path -Path $OutputPath)) {
    New-Item -Path $OutputPath -ItemType Directory | Out-Null
}

Write-Host "Starting checksum-verified integration..." -ForegroundColor Yellow

# 1. Iterate through every song folder in the original library
Get-ChildItem -Path $RootPath -Directory | ForEach-Object {
    $SongFolder = $_
    $SongFolderName = $SongFolder.Name
    
    # 2. Find the MOGG file in the original source folder
    $OriginalMogg = Get-ChildItem -Path $SongFolder.FullName -Filter "*.mogg" -ErrorAction SilentlyContinue | Select-Object -First 1

    if ($OriginalMogg) {
        $MoggFileName = $OriginalMogg.Name
        $FixedMoggPath = Join-Path -Path $FixedMoggSource -ChildPath $MoggFileName

        # 3. Check if a fixed version exists in the 'decrypted' folder
        if (Test-Path -Path $FixedMoggPath) {
            # 4. CRITICAL: Calculate checksums for comparison
            $OriginalHash = Get-FileHashSHA256 $OriginalMogg.FullName
            $FixedHash = Get-FileHashSHA256 $FixedMoggPath

            if ($OriginalHash -ne $FixedHash) {
                # --- CHECKSUMS ARE DIFFERENT: THE FILE WAS FIXED ---

                # 5. Create a clean copy of the song folder in the output path
                $NewSongPath = Join-Path -Path $OutputPath -ChildPath $SongFolderName
                Copy-Item -Path $SongFolder.FullName -Destination $OutputPath -Recurse -Force | Out-Null
                
                # 6. Replace the MOGG file in the new folder with the fixed version
                Copy-Item -Path $FixedMoggPath -Destination (Join-Path -Path $NewSongPath -ChildPath $MoggFileName) -Force
                
                Write-Host "   -> FIXED & COPIED: $SongFolderName (Checksums differ, decryption was needed)" -ForegroundColor Green
                
            } else {
                # --- CHECKSUMS ARE THE SAME: FILE WAS ALREADY DECRYPTED ---
                # Nautilus processed it, but the data did not change. Skip copying.
                Write-Host "   -> SKIPPED: $SongFolderName (Checksums match, no decryption needed)"
            }
        } else {
            # MOGG was not found in the 'decrypted' folder (i.e., Nautilus skipped it completely)
            Write-Host "   -> SKIPPED: $SongFolderName (Nautilus did not output a fixed version)"
        }
    } else {
        Write-Warning ("Skipping {0}: No MOGG file found in original folder." -f $SongFolderName) 
    }
}

# 7. Clean up the temporary folder
Remove-Item -Path $TempPath -Recurse -Force -ErrorAction Stop
Write-Host "----------------------------------------"
Write-Host "Process complete! The output path $OutputPath contains ONLY the verified fixed songs." -ForegroundColor Green
