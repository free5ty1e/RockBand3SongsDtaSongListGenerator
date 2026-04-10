import struct
import sys

def parse_ark(path):
    with open(path, 'rb') as f:
        data = f.read()
    
    offset = 0
    # Skip version (4 bytes)
    version = struct.unpack('<I', data[0:4])[0]
    print(f"Version: {version}")
    offset = 4
    
    while offset + 4 <= len(data):
        try:
            length = struct.unpack('<I', data[offset:offset+4])[0]
            if length == 0:
                print(f"Offset {offset}: length 0")
                offset += 4
                continue
            
            if offset + 4 + length > len(data):
                break
            
            string_data = data[offset+4 : offset+4+length]
            try:
                s = string_data.decode('utf-8')
            except:
                s = str(string_data)
            
            print(f"Offset {offset}: length {length} -> {s}")
            offset += 4 + length
        except Exception as e:
            print(f"Error at offset {offset}: {e}")
            break

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_ark(sys.argv[1])
    else:
        print("Usage: python3 parse_ark.py <path>")
