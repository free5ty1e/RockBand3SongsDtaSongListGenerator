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
    Write-Host "`nUSAGE INSTRUCTIONS: Integrate Fixed MOGGs and Build Library" -ForegroundColor Cyan
    Write-Host "-----------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "This script copies ONLY the folders containing fixed MOGGs to the output path."
    Write-Host "   -RootPath:  The root directory of your original custom song library (used as the source template)."
    Write-Host "   -TempPath:  The temporary directory where Nautilus decrypted the MOGGs (must contain the 'decrypted' subfolder)."
    Write-Host "   -OutputPath: The final, clean directory to store ONLY the fixed songs for the PS3."
    Write-Host "`nExample:" -ForegroundColor Yellow
    Write-Host "  .\integrate_fixed_mogg.ps1 -RootPath 'C:\MyRB3Library\Original_Songs' -TempPath 'C:\RB3DX_Temp_MOGG_Process' -OutputPath 'D:\RB3DX_PS3_Upload\Cleaned_Songs'`n" -ForegroundColor Yellow
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

Write-Host "Starting conditional integration and final copy..."

# 1. Iterate through every song folder in the original library
Get-ChildItem -Path $RootPath -Directory | ForEach-Object {
    $SongFolder = $_
    $SongFolderName = $SongFolder.Name
    
    # 2. Find the MOGG file in the original source folder (for filename)
    $SourceMogg = Get-ChildItem -Path $SongFolder.FullName -Filter "*.mogg" -ErrorAction SilentlyContinue | Select-Object -First 1

    if ($SourceMogg) {
        $MoggFileName = $SourceMogg.Name
        
        # 3. Check if a fixed version exists in the 'decrypted' folder
        $FixedMoggPath = Join-Path -Path $FixedMoggSource -ChildPath $MoggFileName

        if (Test-Path -Path $FixedMoggPath) {
            # *** CORE LOGIC CHANGE: ONLY COPY IF A FIXED FILE EXISTS ***

            # 4. Create a clean copy of the song folder in the output path
            $NewSongPath = Join-Path -Path $OutputPath -ChildPath $SongFolderName
            Copy-Item -Path $SongFolder.FullName -Destination $OutputPath -Recurse -Force | Out-Null
            
            # 5. Replace the MOGG file in the new folder with the fixed version
            Copy-Item -Path $FixedMoggPath -Destination (Join-Path -Path $NewSongPath -ChildPath $MoggFileName) -Force
            
            Write-Host "   -> FIXED: Copied and integrated $SongFolderName (needed decryption)" -ForegroundColor Yellow
            
        } else {
            # MOGG was not found in the 'decrypted' folder, so it was skipped by Nautilus (assumed good).
            Write-Host "   -> SKIPPED: $SongFolderName (Did not require decryption)"
        }
    } else {
        Write-Warning ("Skipping {0}: No MOGG file found in original folder." -f $SongFolderName) 
    }
}

# 6. Clean up the temporary folder
Remove-Item -Path $TempPath -Recurse -Force -ErrorAction Stop
Write-Host "----------------------------------------"
Write-Host "Process complete! The output path $OutputPath contains ONLY the fixed songs." -ForegroundColor Green
