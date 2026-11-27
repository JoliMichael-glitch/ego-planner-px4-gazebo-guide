#!/usr/bin/env python3
"""Restore original mesh/texture assets into this checkout. Existing differing files are refused."""
from pathlib import Path
import tarfile
root=Path(__file__).resolve().parent
with tarfile.open(root/'resources/model-assets.tar.xz', 'r:xz') as archive:
    for entry in archive.getmembers():
        target=(root/entry.name).resolve()
        if not target.is_relative_to(root): raise ValueError('Invalid archive path')
        if not entry.isfile(): raise ValueError('Non-regular archive member')
        data=archive.extractfile(entry).read()
        if target.exists() and target.read_bytes()!=data: raise FileExistsError(target)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
print('Original model assets restored.')
