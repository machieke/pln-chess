"""Lossless compact evidence archives; compression level changes no proof content."""
import json
import lzma
from pathlib import Path

def pack(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    payload=lzma.compress(raw,preset=1)
    assert lzma.decompress(payload)==raw
    temporary=path.with_suffix(path.suffix+'.tmp');temporary.write_bytes(payload);temporary.replace(path)
