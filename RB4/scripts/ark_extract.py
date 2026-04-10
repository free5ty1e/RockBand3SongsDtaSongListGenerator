import os
import struct

def read_uint32_le(f):
    return struct.unpack('<I', f.read(4))[0]

def read_int32_le(f):
    return struct.unpack('<i', f.read(4))[0]

def read_int64_le(f):
    return struct.unpack('<q', f.read(8))[0]

def read_length_utf8(f):
    length = read_uint32_le(f)
    return f.read(length).decode('utf-8', errors='replace')

def read_ascii_null_terminated(f):
    res = b""
    while True:
        char = f.read(1)
        if not char or char == b"\\x00":
            break
        res += char
    return res.decode('ascii', errors='replace')

def extract_ark(ark_path, output_dir):
    with open(ark_path, 'rb') as f:
        version = read_uint32_le(f)
        
        if version == 0x4B5241: # "ARK"
            # Old ark format
            f.seek(8)
            file_table_offset = read_uint32_le(f)
            num_files = read_uint32_le(f)
            dir_table_offset = read_uint32_le(f)
            num_dirs = read_uint32_le(f)
            
            # Read directories
            dirs = []
            for i in range(num_dirs):
                f.seek(dir_table_offset + (8 * i) + 4)
                dir_offset = read_uint32_le(f)
                f.seek(dir_offset)
                dirs.append(read_ascii_null_terminated(f))
            
            # Read files
            for i in range(num_files):
                f.seek(file_table_offset + (24 * i) + 4)
                filename_offset = read_uint32_le(f)
                dir_id = struct.unpack('<H', f.read(2))[0]
                block_offset = struct.unpack('<H', f.read(2))[0]
                block = read_uint32_le(f)
                size = read_uint32_le(f)
                
                f.seek(filename_offset)
                filename = read_ascii_null_terminated(f)
                
                parent_dir = dirs[dir_id] if dir_id < len(dirs) else ""
                out_path = os.path.join(output_dir, parent_dir, filename)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                
                f.seek(0x24)
                block_size = read_uint32_le(f)
                
                f.seek(block * block_size + block_offset)
                with open(out_path, 'wb') as out:
                    out.write(f.read(size))
        
        elif version == 257:
            # Attempt to use a modified Old ark format for version 257
            f.seek(8)
            file_table_offset = read_uint32_le(f)
            num_files = read_uint32_le(f)
            # We don't know dir_table_offset and num_dirs for sure, so let's guess
            dir_table_offset = 0
            num_dirs = 0
            
            # Read files
            for i in range(num_files):
                # Guessing the file table entry size is 24 bytes
                f.seek(file_table_offset + (24 * i))
                # Try to read filename_offset, dir_id, block_offset, block, size
                try:
                    filename_offset = read_uint32_le(f)
                    dir_id = struct.unpack('<H', f.read(2))[0]
                    block_offset = struct.unpack('<H', f.read(2))[0]
                    block = read_uint32_le(f)
                    size = read_uint32_le(f)
                    
                    f.seek(filename_offset)
                    filename = read_ascii_null_terminated(f)
                    
                    parent_dir = ""
                    out_path = os.path.join(output_dir, parent_dir, filename)
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    
                    # Block size guess: 0x10000 (65536)
                    block_size = 65536
                    f.seek(block * block_size + block_offset)
                    with open(out_path, 'wb') as out:
                        out.write(f.read(size))
                except:
                    continue
        
        elif 1 <= version <= 16:
            # New ark format


            if version >= 6:
                f.seek(20, 1) # skip 4+16
            
            if version > 2:
                num_arks = read_int32_le(f)
                print(f"Version: {version}, num_arks: {num_arks}")
                num_arks2 = read_int32_le(f)
                print(f"num_arks2: {num_arks2}")
                # In a real scenario we'd need the other .ark files, but here we only have one?
                # The C# code creates a MultiStream of all .ark files.
                # For simplicity, if we only have one .ark file, we treat it as the only source.
                
                ark_sizes = []
                for i in range(num_arks):
                    size = read_int64_le(f) if version == 4 else read_int32_le(f)
                    ark_sizes.append(size)
                
                if version >= 5:
                    num_paths = read_int32_le(f)
                    # We can ignore the paths for now and just use the current file
                    f.seek(num_paths * 0, 1) # This is wrong, we need to read the strings
                    # Actually, let's just read them to skip
                    for i in range(num_paths):
                        read_length_utf8(f)
                    
                    if 6 <= version <= 9:
                        num_checksums = read_uint32_le(f)
                        f.seek(4 * num_checksums, 1)
                else:
                    # Version < 5: paths are inferred
                    pass
            
            # Now the file table
            if version < 8:
                # read old file table (Version 1, 2)
                # Version 1,2: file records are read.
                # According to ArkPackage.cs:
                # numRecords = header.ReadUInt32LE();
                # header.Close();
                # contentFileMeta = hdrFile.GetStream();
                # contentFileMeta.Seek(8 + numRecords * 20, SeekOrigin.Begin);
                # readFileTable(contentFileMeta, version, brokenv4);
                
                num_records = read_uint32_le(f)
                # In version 1, we skip to the file table
                # Actually, let's try to find where the files are.
                # The C# code says: contentFileMeta.Seek(8 + numRecords * 20, SeekOrigin.Begin);
                # Then it calls readFileTable.
                # In readFileTable:
                # string[] fileNames = readFileNames(header, version != 1);
                # For version 1, nullTerminated = false.
                # readFileNames (nullTerminated=false):
                # fileNameTableSize = header.ReadUInt32LE();
                # string[] strings = new string[fileNameTableSize];
                # for (int i = 0; i < fileNameTableSize; i++)
                #   strings[i] = header.ReadLengthUTF8();
                
                f.seek(8 + num_records * 20)
                
                # read filenames
                filename_table_size = read_uint32_le(f)
                filenames = []
                for i in range(filename_table_size):
                    filenames.append(read_length_utf8(f))
                
                # Now the actual files
                num_files = read_uint32_le(f)
                for i in range(num_files):
                    # Version 1: offset is read at the end
                    # For version != 1, it's read first.
                    #- Read filename pointer
                    #- Read dir pointer
                    #- Read block offset
                    #- Read block
                    #- Read size
                    #- Read zero
                    # - Read offset (for version 1)
                    
                    # Let's try to mimic the C# loop
                    # if (version != 1) arkFileOffset = ...
                    # filenameStringId = readInt32LE();
                    # dirStringId = readInt32LE();
                    # if (version == 1) arkFileOffset = readUInt32LE();
                    # size = readUInt32LE();
                    # zero = readUInt32LE();
                    
                    filename_id = read_int32_le(f)
                    dir_id = read_int32_le(f)
                    ark_offset = read_uint32_le(f)
                    size = read_uint32_le(f)
                    zero = read_uint32_le(f)
                    
                    filename = filenames[filename_id] if filename_id < len(filenames) else "unknown"
                    parent_dir = filenames[dir_id] if dir_id < len(filenames) else ""
                    
                    out_path = os.path.join(output_dir, parent_dir, filename)
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    
                    f.seek(ark_offset)
                    with open(out_path, 'wb') as out:
                        out.write(f.read(size))

            else:
                # read new file table (v9, v10)
                num_files = read_uint32_le(f)
                for i in range(num_files):
                    offset = read_int64_le(f)
                    path = read_length_utf8(f)
                    flags = read_int32_le(f)
                    size = read_uint32_le(f)
                    if version != 10:
                        f.seek(4, 1)
                    
                    out_path = os.path.join(output_dir, path)
                    os.makedirs(os.path.dirname(out_path), exist_ok=True)
                    
                    f.seek(offset)
                    with open(out_path, 'wb') as out:
                        out.write(f.read(size))
                
                # Skip the second flags table
                num_files2 = read_uint32_le(f)
                f.seek(4 * num_files2, 1)

if __name__ == '__main__':
    pass
