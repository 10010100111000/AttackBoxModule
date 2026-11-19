#!/usr/bin/env python3
"""Create or verify the public golden artifact manifest."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re


def checksum(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def validate_version(version):
    if not isinstance(version, str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', version):
        raise ValueError('Version must use three numbers, for example 1.0.0')
    return version


def verify(manifest_path):
    data = json.loads(manifest_path.read_text())
    if not isinstance(data, dict) or data.get('format') != 1 or data.get('subvolume') != 'base_rootfs' or data.get('architecture') != 'amd64':
        raise ValueError('Unsupported golden manifest')
    validate_version(data.get('version'))
    parts = data.get('parts')
    if not isinstance(parts, list) or not 1 <= len(parts) <= 100:
        raise ValueError('Invalid part count')
    paths = []
    for index, part in enumerate(parts):
        name = f'attackbox-golden.btrfs.zst.part-{index:02d}'
        if not isinstance(part, dict) or part.get('name') != name:
            raise ValueError('Invalid part name or order')
        path = manifest_path.parent / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size != part.get('bytes'):
            raise ValueError(f'Missing or wrong-sized part: {name}')
        if checksum(path) != part.get('sha256'):
            raise ValueError(f'Checksum mismatch: {name}')
        paths.append(path.resolve())
    return paths


def create(directory, version, revision):
    validate_version(version)
    if not re.fullmatch(r'[a-f0-9]{40}', revision):
        raise ValueError('Expected a complete Git revision')
    paths = sorted(directory.glob('attackbox-golden.btrfs.zst.part-*'))
    data = {'format': 1, 'version': version, 'subvolume': 'base_rootfs',
            'architecture': 'amd64', 'suite': 'echo', 'revision': revision,
            'upstream': '306a445874d58c836ac7d7a04ec0bc0b2c2547a5',
            'built_at': datetime.now(timezone.utc).isoformat(),
            'parts': [{'name': path.name, 'bytes': path.stat().st_size, 'sha256': checksum(path)} for path in paths]}
    manifest = directory / 'attackbox-golden-manifest.json'
    manifest.write_text(json.dumps(data, indent=2) + '\n')
    verify(manifest)
    (directory / 'attackbox-golden.sha256').write_text(''.join(f'{part["sha256"]}  {part["name"]}\n' for part in data['parts']))
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('create')
    build.add_argument('directory', type=Path)
    build.add_argument('--version', required=True)
    build.add_argument('--revision', required=True)
    check = commands.add_parser('verify')
    check.add_argument('manifest', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'create':
            print(create(args.directory, args.version, args.revision))
        else:
            for path in verify(args.manifest):
                print(path)
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')
