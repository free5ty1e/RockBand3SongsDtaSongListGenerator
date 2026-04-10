import struct
import os
import sys

def decrypt_sng_data(data, seed):
    """
    Decrypts SNG data using the XOR masking algorithm from Nautilus.
    """
    # Generate the 256-byte lookup table from the 16-byte seed
    loop_lookup = bytearray(256)
    for i in range(256):
        loop_lookup[i] = (i ^ seed[i & 0xF]) & 0xFF
    
    # Decrypt data: data[i] ^= loop_lookup[file_pos & 0xFF]
    # According to Nautilus' MaskData, file_pos starts at 0 for each file's content.
    decrypted = bytearray(len(data))
    for i in range(len(data)):
        decrypted[i] = (data[i] ^ loop_lookup[i & 0xFF]) & 0xFF
        
    return bytes(decrypted)

def load_sng_file(path):
    """
    Parses an SNG file and returns its contents and metadata.
    """
    with open(path, 'rb') as f:
        # Header
        identifier = f.read(6)
        if identifier != b"SNGPKG":
            raise ValueError("Invalid SNG file identifier")
        
        version = struct.unpack('<I', f.read(4))[0]
        xor_mask = f.read(16)
        
        # Metadata
        metadata_len = struct.unpack('<Q', f.read(8))[0]
        metadata_count = struct.unpack('<Q', f.read(8))[0]
        
        metadata = {}
        for _ in range(metadata_count):
            key_len = struct.unpack('<i', f.read(4))[0]
            key = f.read(key_len).decode('utf-8', errors='ignore')
            val_len = struct.unpack('<i', f.read(4))[0]
            val = f.read(val_len).decode('utf-8', errors='ignore')
            metadata[key] = val
            
        # File Index
        file_index_len = struct.unpack('<Q', f.read(8))[0]
        file_count = struct.unpack('<Q', f.read(8))[0]
        
        files_info = []
        for _ in range(file_count):
            name_len = f.read(1)[0]
            name = f.read(name_len).decode('utf-8', errors='ignore')
            contents_len = struct.unpack('<Q', f.read(8))[0]
            contents_index = struct.unpack('<Q', f.read(8))[0]
            files_info.append({
                'name': name,
                'len': contents_len,
                'pos': contents_index
            })
            
        file_section_len = struct.unpack('<Q', f.read(8))[0]
        
        # Decrypt files
        decrypted_files = {}
        for info in files_info:
            f.seek(info['pos'])
            raw_data = f.read(info['len'])
            decrypted_data = decrypt_sng_data(raw_data, xor_mask)
            decrypted_files[info['name']] = decrypted_data
            
        return {
            'version': version,
            'metadata': metadata,
            'files': decrypted_files
        }

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 sng_decrypt.py <input_sng> <output_dir>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    try:
        sng = load_sng_file(input_path)
        print(f"Loaded SNG version {sng['version']}")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save metadata as song.ini
        with open(os.path.join(output_dir, "song.ini"), 'w') as f:
            f.write("[song]\n")
            for k, v in sng['metadata'].items():
                f.write(f"{k}={v}\n")
                
        # Save files
        for name, data in sng['files'].items():
            out_path = os.path.join(output_dir, name)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, 'wb') as f:
                f.write(data)
                
        print(f"Successfully decrypted {len(sng['files'])} files to {output_dir}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
