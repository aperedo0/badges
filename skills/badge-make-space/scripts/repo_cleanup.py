"""Apply inspected obsolete artifact lists only in the owner's badge repository."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time

ROOT = Path('/Users/antonioperedo/Desktop/badges')
PROTECTED = {'.git', '.agents', '.codex', '.claude', '.aws', 'skills'}
ROOT_FILES = {'AGENTS.md', 'CLAUDE.md', '.gitignore', '.gitattributes', '.gitmodules'}
ARTIFACTS = {'.blend', '.usdz', '.usdc', '.npz', '.npy', '.png', '.jpg', '.jpeg',
             '.exr', '.mp4', '.mov', '.safe', '.pyc', '.tmp', '.log'}


def inside(relative):
    if not isinstance(relative, str) or not relative or '\x00' in relative:
        raise ValueError('A literal relative filename is required')
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or str(rel) == '.':
        raise ValueError('Path leaves the repository: ' + relative)
    if ROOT.is_symlink() or ROOT.resolve() != ROOT:
        raise ValueError('Repository root must be the expected real directory')
    path = ROOT
    for part in rel.parts:
        path /= part
        if path.is_symlink():
            raise ValueError('Linked paths are protected: ' + relative)
    return path


def writable(relative):
    path = inside(relative)
    rel = path.relative_to(ROOT)
    if {p.casefold() for p in PROTECTED}.intersection(p.casefold() for p in rel.parts) or rel.parts[0].casefold() in {p.casefold() for p in ROOT_FILES}:
        raise ValueError('Protected repository path: ' + relative)
    return path


def fingerprint(relative):
    path = inside(relative)
    if not path.is_file():
        raise ValueError('Expected a regular file: ' + relative)
    before = path.stat()
    with path.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise ValueError('File changed while fingerprinting: ' + relative)
    return {'path': str(path.relative_to(ROOT)), 'bytes': after.st_size,
            'mtime_ns': after.st_mtime_ns, 'sha256': digest}


def verify(row):
    if not isinstance(row, dict):
        raise ValueError('Fingerprint must be an object')
    if not isinstance(row.get('bytes'), int) or not isinstance(row.get('mtime_ns'), int):
        raise ValueError('Size and modification time fingerprints are required')
    if not isinstance(row.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', row['sha256']):
        raise ValueError('A SHA256 fingerprint is required')
    actual = fingerprint(row.get('path'))
    if any(actual[k] != row.get(k) for k in ('path', 'bytes', 'mtime_ns', 'sha256')):
        raise ValueError('Stale fingerprint: ' + str(row.get('path')))
    return inside(actual['path'])


def inventory():
    files = []
    links = []
    git_bytes = 0
    for base, dirs, names in os.walk(ROOT, followlinks=False):
        kept_dirs = []
        for name in dirs:
            p = Path(base) / name
            if p.is_symlink():
                links.append(str(p.relative_to(ROOT)))
            else:
                kept_dirs.append(name)
        dirs[:] = kept_dirs
        for name in names:
            path = Path(base) / name
            rel = path.relative_to(ROOT)
            if path.is_symlink():
                links.append(str(rel)); continue
            stat = path.stat()
            if rel.parts[0] == '.git':
                git_bytes += stat.st_size
            else:
                files.append({'path': str(rel), 'bytes': stat.st_size, 'mtime_ns': stat.st_mtime_ns})
    return {'version': 1, 'root': str(ROOT), 'created_epoch': time.time(),
            'working_bytes': sum(f['bytes'] for f in files), 'git_bytes': git_bytes,
            'free_bytes': shutil.disk_usage(ROOT).free, 'files': files,
            'links_not_followed': links}


def preflight(manifest):
    if manifest.get('version') != 1 or manifest.get('root') != str(ROOT):
        raise ValueError('Manifest is not for this badge repository')
    if not isinstance(manifest.get('authorization'), str) or not manifest['authorization'].strip():
        raise ValueError('Record the actual owner cleanup request')
    keep, remove = manifest.get('keep'), manifest.get('remove')
    if not isinstance(keep, list) or not keep or not isinstance(remove, list):
        raise ValueError('A nonempty keep list and an explicit removal list are required')
    models = manifest.get('models')
    if not isinstance(models, list) or not models:
        raise ValueError('The inspected current model index is required')
    keep_names = set(); remove_names = set(); keep_inodes = set()
    for row in keep:
        path = verify(row)
        if row['path'] in keep_names:
            raise ValueError('Duplicate keep path')
        keep_names.add(row['path'])
        s = path.stat(); keep_inodes.add((s.st_dev, s.st_ino))
    for model in models:
        if not isinstance(model, dict) or not model.get('badge') or not model.get('evidence'):
            raise ValueError('Each model needs its name and selection evidence')
        paths = [model.get(k) for k in ('blender', 'export') if model.get(k)]
        if not paths or any(p not in keep_names for p in paths):
            raise ValueError('Current model files must have keep fingerprints')
    for row in remove:
        if not isinstance(row, dict) or not isinstance(row.get('reason'), str) or not row['reason'].strip():
            raise ValueError('Each removal requires an inspected reason')
        path = writable(row.get('path'))
        if path.suffix.lower() not in ARTIFACTS and path.name != '.DS_Store' and not re.search(r'\.blend[1-9]\d*$', path.name):
            raise ValueError('Source or unknown file type is protected: ' + row['path'])
        if row['path'] in keep_names or row['path'] in remove_names:
            raise ValueError('Overlapping or duplicate removal path')
        verify(row)
        s = path.stat()
        if (s.st_dev, s.st_ino) in keep_inodes:
            raise ValueError('Removal aliases a retained file')
        remove_names.add(row['path'])
    return keep, remove


def apply_manifest(manifest, receipt_relative):
    keep, remove = preflight(manifest)
    receipt = writable(receipt_relative)
    if receipt.suffix != '.jsonl' or receipt.exists():
        raise ValueError('Receipt must be a new JSONL file')
    if receipt_relative in {r['path'] for r in keep + remove}:
        raise ValueError('Receipt overlaps the file lists')
    receipt.parent.mkdir(parents=True, exist_ok=True)
    before = shutil.disk_usage(ROOT).free
    removed_bytes = 0
    with receipt.open('x') as handle:
        def record(value):
            handle.write(json.dumps(value) + '\n'); handle.flush(); os.fsync(handle.fileno())
        record({'event': 'planned', 'epoch': time.time(), 'root': str(ROOT), 'remove': remove})
        try:
            for row in remove:
                path = writable(row['path'])
                verify(row)
                record({'event': 'intent', **row})
                path.unlink()
                removed_bytes += row['bytes']
                record({'event': 'removed', **row})
            for row in keep:
                verify(row)
        except Exception as error:
            try:
                record({'event': 'aborted', 'error': str(error)})
            except OSError:
                pass
            raise
        result = {'event': 'complete', 'removed_files': len(remove), 'logical_removed_bytes': removed_bytes,
                  'free_bytes_before': before, 'free_bytes_after': shutil.disk_usage(ROOT).free,
                  'retained_fingerprints_verified': len(keep)}
        record(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    scan = sub.add_parser('inventory'); scan.add_argument('--out', required=True)
    apply = sub.add_parser('apply'); apply.add_argument('manifest'); apply.add_argument('--receipt', required=True)
    args = parser.parse_args()
    if args.command == 'inventory':
        out = writable(args.out)
        if out.suffix != '.json' or out.exists():
            raise ValueError('Inventory output must be a new JSON file')
        data = inventory(); out.parent.mkdir(parents=True, exist_ok=True)
        with out.open('x') as handle:
            json.dump(data, handle, indent=2); handle.write('\n')
        print(json.dumps({k: v for k, v in data.items() if k not in ('files', 'links_not_followed')}))
    else:
        source = inside(args.manifest)
        print(json.dumps(apply_manifest(json.loads(source.read_text()), args.receipt)))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
