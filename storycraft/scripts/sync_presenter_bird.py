#!/usr/bin/env python3
"""Import the *original* Gilded riding-bird PNG from Drift Map Presenter.

Usage:
  python scripts/sync_presenter_bird.py
  python scripts/sync_presenter_bird.py --download

By default, copy only from an existing installed sibling skill. The --download
flag explicitly opts into downloading the public, pinned GitHub asset. Rendering
story HTML itself never makes network requests.
"""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import shutil
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets' / 'gilded-bird.png'
URL = 'https://raw.githubusercontent.com/peteralmoreno/agent-skills/main/driftmap-presenter/assets/gilded-bird.png'
GIT_BLOB_SHA1 = 'd8c10c7f485c1e7ff2c4cbf946344ec0609cf269'


def is_original(data: bytes) -> bool:
    if not (data.startswith(b'\x89PNG\r\n\x1a\n') and len(data) < 4_000_000):
        return False
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == GIT_BLOB_SHA1


def local_paths() -> list[Path]:
    import os
    paths = []
    folders = ('driftmap-presenter', 'presenter-driftmap')
    dirs = [ROOT.parent, Path.cwd(), Path.cwd()/'agent-skills']
    for home in (Path.home(), Path(os.environ.get('USERPROFILE') or str(Path.home()))):
        dirs.extend([home/'.agents'/'skills', home/'.claude'/'skills',home/'.omp'/'skills'])
    for home in (ROOT.parent, Path.cwd()):
        dirs.extend([home/'.agents'/'skills', home/'.claude'/'skills',home/'.omp'/'skills'])
    for d in dirs:
        for folder in folders:
            p = d/folder/'assets'/'gilded-bird.png'
            if p not in paths: paths.append(p)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true', help='Explicitly fetch original PNG from pinned public GitHub path if not found locally')
    parser.add_argument('--force', action='store_true', help='Replace an existing noncanonical file after validation')
    args = parser.parse_args()
    if DEST.exists() and is_original(DEST.read_bytes()) and not args.force:
        print('Original Presenter bird already bundled:', DEST)
        return 0
    if DEST.exists() and not args.force:
        print('Existing asset is not canonical. Inspect it before rerunning with --force:', DEST, file=sys.stderr)
        return 1
    data = None
    for path in local_paths():
        if path.is_file() and is_original(path.read_bytes()):
            print('Importing original Presenter artwork from', path)
            data = path.read_bytes()
            break
    if data is None and args.download:
        try:
            with urlopen(Request(URL, headers={'User-Agent': 'storycraft-skill-asset-import/0.4'}), timeout=20) as response:
                data = response.read(4_000_001)
        except Exception as exc:
            print('Unable to download:', exc, file=sys.stderr)
            return 1
    if data is None:
        print('Original PNG not found in installed sibling skill. Rerun with --download to opt into fetching it from GitHub.')
        return 2
    if not is_original(data):
        print('Downloaded or local PNG does not match the expected original Git blob. Refusing to use it.', file=sys.stderr)
        return 1
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(data)
    print('Imported original Presenter artwork:', DEST, f'({len(data):,} bytes)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
