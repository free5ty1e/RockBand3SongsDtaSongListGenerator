# 🚀 Rock Band 3 Deluxe: Encrypted MOGG Fix Workflow

This guide details a reliable, three-step workflow to identify and fix custom songs in your library that fail to load (hang on the loading screen) due to **encrypted MOGG audio files**. This process leverages the **Nautilus Batch Cryptor** tool and two custom PowerShell scripts to efficiently process a large library.

---

## 🎯 The Problem

Many older custom songs or CON file exports feature MOGG audio files that are **encrypted** or wrapped in a format that *Rock Band 3 Deluxe* on PS3 cannot read. This typically results in:

1.  The song failing to play an audio preview in the song list.
2.  The game hanging indefinitely on the loading screen when the song is selected.

---

## 🛠️ Prerequisites

Before starting, ensure you have the following:

1.  **Nautilus Tool (formerly C3 CON Tools):** This Windows utility is required to perform the batch decryption.
2.  **PowerShell:** The scripts provided below require **Windows PowerShell** (version 3.0 or later).
3.  **Source Library:** Your full custom song library in one root directory (e.g., `C:\MyRB3Library\Original_Songs`).
4.  **Working Directory:** A separate drive or directory with sufficient free space to handle the temporary files and the final output.

---

## 🔄 The Three-Step Workflow

This workflow is designed to be safe, creating a new, clean output directory containing **only** the fixed songs, leaving your original library untouched.

### Step 1: Extract All MOGG Files to a Temp Folder (Script 1)

This script flattens your entire library's MOGG files into one temporary location so Nautilus can process them all at once.

#### **Script 1: `copy_mogg_to_temp.ps1`**

| Parameter | Description |
| :--- | :--- |
| **`-RootPath`** | **Mandatory.** The root directory of your entire custom song library. |
| **`-TempPath`** | **Mandatory.** The temporary directory where MOGG files will be copied for Nautilus. |

**Execution Example:**
\`\`\`powershell
.\copy_mogg_to_temp.ps1 -RootPath 'C:\MyRB3Library\Original_Songs' -TempPath 'C:\RB3DX_Temp_MOGG_Process'
\`\`\`

---

### Step 2: Batch Decrypt the MOGG Files (Nautilus)

Run the Nautilus tool on the temporary folder to decrypt any encrypted MOGG files.

1.  Open **Nautilus** and navigate to the **Batch Cryptor** tab.
2.  Set the mode to **Decrypt**.
3.  Click the **"Select Folder"** button and choose the temporary folder created in Step 1 (e.g., `C:\RB3DX_Temp_MOGG_Process`).
4.  Click **Begin**.

⚠️ **Crucial Result:** Nautilus will decrypt the fixed files and place them in a new subfolder: `C:\RB3DX_Temp_MOGG_Process\decrypted\`. Only MOGG files that *needed* fixing will be in this new subfolder.

---

### Step 3: Integrate Fixed MOGGs and Build Final Library (Script 2)

This script is selective: it iterates through your original library, checks if a fixed MOGG exists in the `decrypted` folder, and **only copies the entire song folder** to the output if a fix was applied. It also deletes the temporary folder.

#### **Script 2: `integrate_fixed_mogg.ps1`**

| Parameter | Description |
| :--- | :--- |
| **`-RootPath`** | **Mandatory.** The original song library path (used as the template for file structure). |
| **`-TempPath`** | **Mandatory.** The temporary directory containing the `decrypted` subfolder. |
| **`-OutputPath`** | **Mandatory.** The final, clean directory to store **ONLY** the fixed songs for the PS3. |

**Execution Example:**
\`\`\`powershell
.\integrate_fixed_mogg.ps1 -RootPath 'C:\MyRB3Library\Original_Songs' -TempPath 'C:\RB3DX_Temp_MOGG_Process' -OutputPath 'D:\RB3DX_PS3_Upload\Cleaned_Songs'
\`\`\`

**Output:** The folder `D:\RB3DX_PS3_Upload\Cleaned_Songs` will contain **only** the song folders that required MOGG decryption, ready for upload to your PS3. The script also cleans up and deletes the temporary folder (`C:\RB3DX_Temp_MOGG_Process`).

---

## 💡 Troubleshooting & Usage Notes

* **Execution Policy:** If PowerShell blocks the script, you may need to run this command once to allow local script execution: `Set-ExecutionPolicy RemoteSigned`.
* **Mandatory Parameters:** If you run either script without providing all mandatory parameters, it will automatically display the detailed usage instructions. You can also explicitly request usage by running: `.\script_name.ps1 -?`.
* **Case Sensitivity:** PS3/Linux file systems are **case-sensitive**. Ensure the capitalization in your `songs.dta` matches your folder names exactly!

