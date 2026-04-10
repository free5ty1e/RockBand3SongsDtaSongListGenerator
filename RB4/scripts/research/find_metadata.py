with open('/workspace/rb4_temp/base_game_extract/main_ps4_0.ark', 'rb') as f:
    content = f.read()
    offsets = []
    pos = content.find(b"RBSongMetadata")
    while pos != -1:
        offsets.append(pos)
        pos = content.find(b"RBSongMetadata", pos + 1)
    for o in offsets[:5]:
        print(f"Found at {o}")
    print(f"Total found: {len(offsets)}")
