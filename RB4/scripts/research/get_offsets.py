with open('/workspace/rb4_temp/base_game_extract/main_ps4_10.ark', 'rb') as f:
    content = f.read()
    pos = content.find(b"RBSongMetadata")
    while pos != -1:
        print(pos)
        pos = content.find(b"RBSongMetadata", pos + 1)
