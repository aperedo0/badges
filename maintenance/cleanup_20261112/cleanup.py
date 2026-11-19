"""Owner authorized folder cleanup. Preserve every retained file's exact bytes.

This is confined to the badges workspace. It does not clean the Mac globally,
touch Git storage, restart badge work, or remove any candidate directory.
Duplicate files use APFS copy on write clones, never hard links. Future edits
remain independent. Only redundant automatic Blender backups and reproducible
Python bytecode are deleted.
"""
from pathlib import Path
import ctypes
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
assert ROOT == Path('/Users/antonioperedo/Desktop/badges')
INVENTORY = json.loads((HERE / 'inventory.json').read_text())
TRACKED = set(subprocess.check_output(
    ['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0'))
LIBC = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
LIBC.clonefile.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
LIBC.clonefile.restype = ctypes.c_int
CUTOFF = time.time() - 1800
REPORT = dict(started=datetime.datetime.now().astimezone().isoformat(),
              free_before=shutil.disk_usage(ROOT).free,
              cloned=[], deleted=[], skipped=[], failures=[])


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def safe(relative):
    p = ROOT / relative
    assert p.resolve() == p and p.is_relative_to(ROOT) and p != ROOT
    assert not any(x in p.relative_to(ROOT).parts for x in
                   ['.git', '.agents', '.codex', '.aws', '.xcodebuildmcp'])
    assert p.is_file() and not p.is_symlink()
    return p


def unchanged(path, st):
    now = path.stat()
    return (now.st_ino, now.st_size, now.st_mtime_ns) == (
        st.st_ino, st.st_size, st.st_mtime_ns)


def clone(source, target):
    result = LIBC.clonefile(os.fsencode(source), os.fsencode(target), 1)
    if result:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err), str(target))


def write_report():
    REPORT['free_after'] = shutil.disk_usage(ROOT).free
    tmp = HERE / 'report.json.tmp'
    tmp.write_text(json.dumps(REPORT, indent=2) + '\n')
    os.replace(tmp, HERE / 'report.json')


# Prove that the filesystem supports clones and that writes stay independent.
test_source = HERE / '.clone_probe_original'
test_copy = HERE / '.clone_probe_copy'
try:
    test_source.write_bytes(b'original badge storage probe')
    clone(test_source, test_copy)
    assert test_source.stat().st_ino != test_copy.stat().st_ino
    test_copy.write_bytes(b'independent edit')
    assert test_source.read_bytes() == b'original badge storage probe'
    REPORT['copy_on_write_independence_proved'] = True
finally:
    test_copy.unlink(missing_ok=True)
    test_source.unlink(missing_ok=True)

for number, group in enumerate(INVENTORY['duplicates']):
    paths = [safe(p) for p in group['paths'] if not p.endswith('.blend1')]
    if len(paths) < 2:
        continue
    # Keep original assets as anchors and replace the storage of their copies.
    paths.sort(key=lambda p: (
        0 if 'mobile' in p.parts else 1 if 'source' in p.parts else 2,
        str(p)))
    source = paths[0]
    source_stat = source.stat()
    if source_stat.st_mtime > CUTOFF or digest(source) != group['hash']:
        REPORT['skipped'].append(dict(path=str(source.relative_to(ROOT)),
                                      reason='Recent or changed anchor'))
        continue
    for target in paths[1:]:
        rel = str(target.relative_to(ROOT))
        st = target.stat()
        if st.st_mtime > CUTOFF or st.st_nlink > 1:
            REPORT['skipped'].append(dict(path=rel, reason='Recent or linked'))
            continue
        temporary = target.parent / ('.storage_clone_' + uuid.uuid4().hex)
        try:
            assert unchanged(source, source_stat)
            assert digest(target) == group['hash']
            clone(source, temporary)
            assert temporary.stat().st_ino != source.stat().st_ino
            assert digest(temporary) == group['hash']
            shutil.copystat(target, temporary, follow_symlinks=False)
            assert unchanged(target, st) and unchanged(source, source_stat)
            os.replace(temporary, target)
            assert digest(target) == group['hash']
            REPORT['cloned'].append(dict(path=rel,
                anchor=str(source.relative_to(ROOT)), bytes=st.st_size,
                sha256=group['hash'], exact_bytes_verified=True))
        except Exception as error:
            REPORT['failures'].append(dict(path=rel, error=str(error)))
        finally:
            temporary.unlink(missing_ok=True)
    if number % 40 == 0:
        write_report()
        print('Verified duplicate groups:', number, flush=True)

for _, relative in INVENTORY['backups']:
    p = safe(relative)
    current = safe(str(p.with_suffix('.blend').relative_to(ROOT)))
    st, current_stat = p.stat(), current.stat()
    if relative in TRACKED or st.st_mtime > CUTOFF:
        REPORT['skipped'].append(dict(path=relative,
                                      reason='Tracked or recent backup'))
        continue
    with current.open('rb') as f:
        header = f.read(12)
    recognizable = (header.startswith(b'BLENDER') or
                    header.startswith(bytes.fromhex('28b52ffd')) or
                    header.startswith(bytes.fromhex('1f8b')))
    if (not recognizable or current_stat.st_size < max(1024 * 1024, st.st_size // 4)
            or current_stat.st_mtime < st.st_mtime):
        REPORT['skipped'].append(dict(path=relative,
                                      reason='Current Blender source not confirmed'))
        continue
    backup_hash, current_hash = digest(p), digest(current)
    assert unchanged(p, st) and unchanged(current, current_stat)
    p.unlink()
    assert digest(current) == current_hash
    REPORT['deleted'].append(dict(path=relative, bytes=st.st_size,
        sha256=backup_hash, reason='Automatic prior save; newer working source kept',
        retained=str(current.relative_to(ROOT)), retained_sha256=current_hash))

for base, dirs, files in os.walk(ROOT, followlinks=False):
    dirs[:] = [d for d in dirs if d not in
        ['.git', '.agents', '.codex', '.aws', '.xcodebuildmcp']
        and not (Path(base) / d).is_symlink()]
    if Path(base).name != '__pycache__':
        continue
    for name in files:
        if not name.endswith('.pyc'):
            continue
        p = Path(base) / name
        relative = str(p.relative_to(ROOT))
        if p.is_symlink() or relative in TRACKED:
            continue
        source = p.parent.parent / (name.split('.cpython-')[0] + '.py')
        if not source.is_file() or p.stat().st_mtime > CUTOFF:
            continue
        st = p.stat()
        p.unlink()
        REPORT['deleted'].append(dict(path=relative, bytes=st.st_size,
                                     reason='Reproducible Python bytecode'))

REPORT['finished'] = datetime.datetime.now().astimezone().isoformat()
REPORT['files_cloned'] = len(REPORT['cloned'])
REPORT['logical_duplicate_bytes_shared'] = sum(x['bytes'] for x in REPORT['cloned'])
REPORT['files_deleted'] = len(REPORT['deleted'])
REPORT['logical_bytes_deleted'] = sum(x['bytes'] for x in REPORT['deleted'])
write_report()
print(json.dumps({k: v for k, v in REPORT.items()
                  if k not in ['cloned', 'deleted', 'skipped', 'failures']}, indent=2))
print('Failures:', len(REPORT['failures']), 'Skipped:', len(REPORT['skipped']), flush=True)
