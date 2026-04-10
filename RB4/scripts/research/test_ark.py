import os
from ark_extract import extract_ark

ark_path = '/workspace/rb4_temp/base_game_extract/main_ps4_0.ark'
output_dir = '/workspace/rb4_temp/ark_test'
os.makedirs(output_dir, exist_ok=True)
try:
    extract_ark(ark_path, output_dir)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
