import os

targets = {
    "The Distance": b"The Distance",
    "Carry On Wayward Son": b"Carry On Wayward Son",
    "Since U Been Gone": b"Since U Been Gone",
    "Hold On": b"Hold On"
}

ark_dir = "/workspace/rb4_temp/base_game_extract"
for f in os.listdir(ark_dir):
    if f.endswith('.ark'):
        path = os.path.join(ark_dir, f)
        with open(path, 'rb') as file:
            content = file.read()
            for name, bytes_seq in targets.items():
                pos = content.find(bytes_seq)
                if pos != -1:
                    print(f"Found '{name}' in {f} at offset {pos}")
