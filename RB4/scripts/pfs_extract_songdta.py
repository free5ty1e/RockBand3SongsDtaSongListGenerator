#!/usr/bin/env python3
"""Sequentially extract .songdta_ps4 files from an (unencrypted) PFS image.

PkgTool's pfs_extract fails on some PFS images that contain duplicate directory
entries (two dirents with the same name in one directory, e.g. a song dir listed
twice), because its parallel extractor opens every output file with
FileShare.None and the two copies collide ("file is being used by another
process"). This tool walks the PFS tree sequentially, so duplicate entries are
harmless (first one wins). Only the .songdta_ps4 files are written, which is
all the RB4 pipeline needs.

Usage:
    pfs_extract_songdta.py <inner.pfs> <output_dir> [--verbose]
"""

import os
import struct
import sys

BLOCK_SIZE = 0x10000
DIR_FILE = 2
DIR_DIR = 3
DIR_DOT = 4
DIR_DOTDOT = 5


class PfsError(Exception):
    pass


class Inode(object):
    __slots__ = ('mode', 'nlink', 'flags', 'size', 'size_compressed',
                 'blocks', 'start_block', 'db', 'ib')


def main():
    args = [a for a in sys.argv[1:]]
    verbose = '--verbose' in args
    args = [a for a in args if a != '--verbose']
    if len(args) != 2:
        print(__doc__)
        return 1
    pfs_path, out_dir = args
    pfs = Pfs(pfs_path)
    files = pfs.list_files(verbose)
    found = 0
    seen = set()
    for path, inode_num in files:
        if not path.endswith('.songdta_ps4'):
            continue
        if path in seen:
            if verbose:
                print(f"skipping duplicate: {path}")
            continue
        seen.add(path)
        dest = os.path.join(out_dir, path.lstrip('/'))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        pfs.extract_file(inode_num, dest)
        found += 1
    print(f"Extracted {found} .songdta_ps4 files to {out_dir}")
    return 0


class Pfs(object):
    def __init__(self, path):
        self.path = path
        self.fh = open(path, 'rb')
        hdr = self.fh.read(0x400)
        version, magic, ident = struct.unpack_from('<qqq', hdr, 0)
        if version != 1 or magic != 20130315:
            raise PfsError('Invalid PFS superblock (bad magic)')
        mode = struct.unpack_from('<H', hdr, 28)[0]
        self.mode = mode
        if mode & 0x4:
            raise PfsError('Encrypted PFS not supported')
        if mode & 0x2:
            raise PfsError('64-bit PFS not supported')
        block_size, nbackup = struct.unpack_from('<II', hdr, 32)
        nblock, dinode_count, ndblock, dinode_block_count = struct.unpack_from('<qqqq', hdr, 40)
        self.block_size = block_size or BLOCK_SIZE
        self.signed = bool(mode & 0x1)
        self.dinode_size = 0x2C8 if self.signed else 0xA8
        self.dinodes = self._read_dinodes(block_size, dinode_count, dinode_block_count)

    def _read_dinodes(self, block_size, dinode_count, dinode_block_count):
        fh = self.fh
        ds = self.dinode_size
        dinodes = []
        total = 0
        fh.seek(block_size)
        for i in range(dinode_block_count):
            block = fh.read(block_size)
            if not block:
                break
            for j in range(block_size // ds):
                if total >= dinode_count:
                    break
                off = j * ds
                d = Inode()
                d.mode, d.nlink, d.flags = struct.unpack_from('<HHI', block, off)
                d.size, d.size_compressed = struct.unpack_from('<qq', block, off + 8)
                d.blocks = struct.unpack_from('<I', block, off + 96)[0]
                if self.signed:
                    d.db = [struct.unpack_from('<i', block, off + 100 + 36 * i + 32)[0] for i in range(12)]
                    d.ib = [struct.unpack_from('<i', block, off + 100 + 36 * 12 + 36 * i + 32)[0] for i in range(5)]
                else:
                    d.db = list(struct.unpack_from('<12i', block, off + 100))
                    d.ib = list(struct.unpack_from('<5i', block, off + 148))
                d.start_block = d.db[0]
                dinodes.append(d)
                total += 1
        return dinodes

    def _read_dirents(self, ino):
        if ino.start_block < 1 or ino.blocks < 1:
            return []
        fh = self.fh
        block_size = self.block_size
        out = []
        for x in range(ino.start_block, ino.start_block + ino.blocks):
            fh.seek(block_size * x)
            block = fh.read(block_size)
            if not block:
                break
            pos = 0
            while pos < block_size:
                inode_num, dtype, name_len, entsize = struct.unpack_from('<Iiii', block, pos)
                if entsize == 0:
                    break
                name = block[pos + 16:pos + 16 + name_len].decode('ascii', errors='replace')
                out.append((dtype, inode_num, name))
                pos += entsize
        return out

    def list_files(self, verbose=False):
        dinodes = self.dinodes
        seen = set()

        def walk(ino, prefix):
            if not ino or ino.start_block in seen:
                return
            seen.add(ino.start_block)
            for dtype, inode_num, name in self._read_dirents(ino):
                if dtype == DIR_FILE:
                    yield prefix + '/' + name, inode_num
                elif dtype == DIR_DIR and inode_num < len(dinodes):
                    for item in walk(dinodes[inode_num], prefix + '/' + name):
                        yield item

        return list(walk(dinodes[0], ''))

    def _block_offsets(self, ino, size):
        block_size = self.block_size
        if ino.start_block >= 0:
            contiguous = True
            if ino.blocks > 1 and ino.db[1] != -1:
                contiguous = False
            if contiguous:
                base = ino.start_block * block_size
                return [base + i * block_size for i in range((size + block_size - 1) // block_size)]
        offsets = []
        for b in ino.db:
            if b == -1 or b < 1:
                break
            offsets.append(b * block_size)
        return offsets

    def extract_file(self, inode_num, dest):
        ino = self.dinodes[inode_num]
        size = ino.size
        fh = self.fh
        block_size = self.block_size
        offsets = self._block_offsets(ino, size)
        if not offsets:
            raise PfsError(f'cannot resolve blocks for inode {inode_num}')
        with open(dest, 'wb') as out:
            remaining = size
            for off in offsets:
                if remaining <= 0:
                    break
                fh.seek(off)
                chunk = fh.read(min(block_size, remaining))
                out.write(chunk)
                remaining -= len(chunk)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except PfsError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
