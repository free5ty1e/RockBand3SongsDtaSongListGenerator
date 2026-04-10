import struct
import os

class EncryptedReadStream:
    def __init__(self, file_handle, xor=0):
        self.file = file_handle
        self.xor = xor
        
        # The initial key is found in the first 4 bytes
        self.file.seek(0)
        initial_key_bytes = self.file.read(4)
        if len(initial_key_bytes) < 4:
            raise IOError("File too short to read initial key")
            
        raw_key = struct.unpack('<i', initial_key_bytes)[0]
        self.key = self._crypt_round(raw_key)
        self.position = 0
        self.keypos = 0
        self.cur_key = self.key
        self.Length = os.path.getsize(file_handle.name) - 4
        self.xor = xor
        
        # The initial key is found in the first 4 bytes
        self.file.seek(0)
        initial_key_bytes = self.file.read(4)
        if len(initial_key_bytes) < 4:
            raise IOError("File too short to read initial key")
            
        self.key = struct.unpack('<i', initial_key_bytes)[0]
        self.cur_key = self.key
        self.position = 0
        self.keypos = 0
        # Length is file length minus the 4-byte key
        self.length = os.path.getsize(file_handle.name) - 4

    def _crypt_round(self, key):
        ret = (key - ((key // 0x1F31D) * 0x1F31D)) * 0x41A7 - (key // 0x1F31D) * 0xB14
        if ret <= 0:
            ret += 0x7FFFFFFF
        # Ensure we stay within 32-bit signed integer range
        return struct.unpack('<i', struct.pack('<i', ret))[0]

    def _update_key(self):
        if self.keypos == self.position:
            return
        if self.keypos > self.position:
            self.keypos = 0
            self.cur_key = self.key
        
        while self.keypos < self.position:
            self.cur_key = self._crypt_round(self.cur_key)
            self.keypos += 1

    def read(self, count):
        if self.position >= self.length:
            return b""
        
        if self.position + count > self.length:
            count = self.length - self.position
            
        # Read from the underlying file at position + 4
        self.file.seek(self.position + 4)
        buffer = bytearray(self.file.read(count))
        
        for i in range(len(buffer)):
            # XOR with (curKey ^ xor)
            buffer[i] ^= (self.cur_key ^ self.xor) & 0xFF
            self.position += 1
            self._update_key()
            
        return bytes(buffer)

    def seek(self, offset, origin=0): # 0: Begin, 1: Current, 2: End
        if origin == 0:
            self.position = offset
        elif origin == 1:
            self.position += offset
        elif origin == 2:
            self.position = self.length + offset
        
        self.position = max(0, min(self.position, self.length))
        self._update_key()
        return self.position

class BinReader:
    def __init__(self, stream):
        self.stream = stream
        
    def read_int(self):
        return struct.unpack('<i', self.stream.read(4))[0]
        
    def read_uint(self):
        return struct.unpack('<I', self.stream.read(4))[0]
        
    def read_long(self):
        return struct.unpack('<q', self.stream.read(8))[0]
        
    def read_string(self):
        # Based on LibForge's BinReader (not shown, but common in these tools)
        # Usually: length (int) followed by bytes
        length = self.read_int()
        if length == 0: return ""
        return self.stream.read(length).decode('utf-8', errors='ignore')

    def read_arr_uint(self):
        count = self.read_int()
        return [self.read_uint() for _ in range(count)]

    def read_arr_string(self):
        count = self.read_int()
        return [self.read_string() for _ in range(count)]

    def read_arr_strings_nested(self):
        count = self.read_int()
        res = []
        for _ in range(count):
            res.append(self.read_arr_string())
        return res

if __name__ == "__main__":
    # Quick test with a base game ark
    ark_path = '/workspace/rb4_temp/base_game_extract/main_ps4_0.ark'
    if os.path.exists(ark_path):
        with open(ark_path, 'rb') as f:
            ers = EncryptedReadStream(f)
            br = BinReader(ers)
            version = br.read_int()
            print(f"Version: {version}")
