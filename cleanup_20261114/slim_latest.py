"""Plan cleanup of superseded attempts while preserving current assets and Git."""
from pathlib import Path
import collections
import ctypes
import ctypes.util
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
AUDIT = Path(__file__).resolve().parent
EXTS = {'.blend', '.usdz', '.usdc', '.npz', '.npy', '.safe', '.png', '.jpg', '.jpeg', '.exr', '.mp4', '.mov', '.zip'}

def blend_bytes(path):
    data = path.read_bytes()
    if data.startswith(b'BLENDER'):
        return data
    if data.startswith(b'\x1f\x8b'):
        return gzip.decompress(data)
    lib = ctypes.CDLL(ctypes.util.find_library('zstd'))
    for name in ('ZSTD_findFrameCompressedSize', 'ZSTD_getFrameContentSize'):
        fn = getattr(lib, name)
        fn.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        fn.restype = ctypes.c_ulonglong
    lib.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
    lib.ZSTD_decompress.restype = ctypes.c_size_t
    src = ctypes.create_string_buffer(data)
    offset = 0
    chunks = []
    while offset < len(data):
        ptr = ctypes.addressof(src) + offset
        size = lib.ZSTD_findFrameCompressedSize(ptr, len(data) - offset)
        length = lib.ZSTD_getFrameContentSize(ptr, size)
        if size > len(data) - offset or length > 512_000_000:
            raise ValueError('Unrecognized Blender compression')
        dst = ctypes.create_string_buffer(length)
        actual = lib.ZSTD_decompress(dst, length, ptr, size)
        if actual != length:
            raise ValueError('Blender decompression failed')
        chunks.append(dst.raw)
        offset += size
    return b''.join(chunks)

def plan():
    files = json.loads(Path('/private/tmp/badges_slim_inventory.json').read_text())
    groups = collections.defaultdict(dict)
    for f in files:
        parts = Path(f['path']).parts
        for i, name in enumerate(parts):
            m = re.fullmatch(r'candidate(\d+)(?:_\w+)?', name)
            if m:
                groups['/'.join(parts[:i])][name] = int(m[1])
                break
    chosen = {g: max(ns, key=lambda k: (ns[k], k)) for g, ns in groups.items()}
    for p in ROOT.rglob('candidate.txt'):
        if '.git' in p.parts:
            continue
        group = str(p.parent.relative_to(ROOT))
        value = p.read_text().strip()
        if value in groups.get(group, {}):
            chosen[group] = value
    current = {g + '/' + value for g, value in chosen.items()}
    for p in ROOT.glob('*/schedule.json'):
        try:
            badges = json.loads(p.read_text()).get('badges', {})
        except (ValueError, OSError):
            continue
        for badge in badges.values() if isinstance(badges, dict) else badges:
            if not isinstance(badge, dict) or not isinstance(badge.get('candidate'), str):
                continue
            q = Path(badge['candidate'])
            q = q if q.is_absolute() else p.parent / q
            if q.is_dir() and q.is_relative_to(ROOT):
                current.add(str(q.relative_to(ROOT)))
    protected = ('ruby_heart_gem_20261113/source/', 'ruby_heart_gem_20261113/mobile/',
                 'ruby_heart_smooth_20261112/ruby_heart.blend', 'emerald_trophy_20261025/preview/')
    deletions = {}
    for f in files:
        rel = f['path']; p = Path(rel); ext = p.suffix.lower(); parts = p.parts
        if rel.startswith(protected):
            continue
        old = False
        for i, name in enumerate(parts):
            if re.fullmatch(r'candidate\d+(?:_\w+)?', name):
                old = '/'.join(parts[:i+1]) not in current
                break
        archive = any(re.match(r'(baseline|previous|scripts_before|runtime_backup|import_backup|backup_)(?:\d|_|$)', v) for v in parts[:-1])
        reason = None
        if ext in EXTS and (old or archive):
            reason = 'Superseded attempt output; current models, source and notes retained'
        if ext in {'.mp4', '.mov'}:
            reason = 'Disposable test recording'
        if ext in {'.png', '.jpg', '.jpeg'}:
            capture = any(v.lower() in {'app', 'review', 'review_baseline', 'blender_zoom', 'blender', 'optics', 'finish_diagnosis'} for v in parts[:-1]) or any(t in p.stem.lower() for t in ('comparison', 'all_views', 'all_sides', 'close_', 'outline', 'zoom', 'viewport', 'motion_review', 'native_front_precheck', 'readiness', 'side_by_side', 'finish_full', 'finish_2x', 'finish_4x'))
            material = any(t in p.stem.lower() for t in ('reference', 'mockup', 'color', 'albedo', 'roughness', 'emission', 'normal', 'target', 'mask', 'palette')) or any(v.lower() in {'textures', 'texture', 'trace', 'source', 'references', 'owner_examples_20261114'} for v in parts[:-1])
            if capture and not material:
                reason = 'Disposable screenshot or enlarged review image'
        if re.search(r'\.blend\d+$', p.name):
            reason = 'Automatic Blender backup'
        if ext == '.pyc' or p.name == '.DS_Store':
            reason = 'Disposable cache'
        if reason:
            deletions[rel] = {**f, 'reason': reason}
    # Inspect retained Blender files without launching Blender or modifying its scene.
    dependencies = set()
    inspected = []
    failures = []
    for f in files:
        rel = f['path']
        if Path(rel).suffix != '.blend' or rel in deletions:
            continue
        p = ROOT / rel
        try:
            raw = blend_bytes(p)
            for token in re.findall(rb'(?:/Users/antonioperedo/Desktop/badges/|//)[^\x00\r\n]{1,1024}?\.(?:png|jpe?g|exr|usdz|blend)', raw, re.I):
                value = token.decode('utf8', errors='ignore')
                q = (p.parent / value[2:]) if value.startswith('//') else Path(value)
                q = q.resolve()
                if q.is_file() and q.is_relative_to(ROOT):
                    dependencies.add(str(q.relative_to(ROOT)))
            inspected.append(rel)
        except Exception as error:
            failures.append({'path': rel, 'error': str(error)})
    if failures:
        raise RuntimeError('Cannot verify retained Blender dependencies: ' + json.dumps(failures))
    for rel in dependencies:
        deletions.pop(rel, None)
    result = {'current_candidates': sorted(current), 'retained_blends_inspected': inspected,
              'blender_dependencies_preserved': sorted(dependencies), 'delete': list(deletions.values())}
    (AUDIT / 'latest_only_plan.json').write_text(json.dumps(result, indent=2) + '\n')
    removed = sum(f['bytes'] for f in deletions.values())
    print(json.dumps({'files_to_remove': len(deletions), 'remove_GB': removed / 1e9,
                      'working_GB_after': (sum(f['bytes'] for f in files) - removed) / 1e9,
                      'blends_inspected': len(inspected), 'dependencies_preserved': len(dependencies)}))

def apply():
    plan = json.loads((AUDIT / 'latest_only_plan.json').read_text())
    tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0'))
    removed = []; skipped = []; before = shutil.disk_usage(ROOT).free
    for item in plan['delete']:
        p = ROOT / item['path']
        if not p.is_file() or p.is_symlink():
            continue
        if not p.is_relative_to(ROOT) or any(v in p.parts for v in ('.git', '.codex', '.agents', '.aws')):
            raise RuntimeError('Protected path')
        if p.stat().st_size != item['bytes']:
            skipped.append(item['path']); continue
        with p.open('rb') as handle:
            digest = hashlib.file_digest(handle, 'sha256').hexdigest()
        p.unlink()
        removed.append({**item, 'sha256': digest, 'tracked': item['path'] in tracked})
    result = {'removed': removed, 'skipped_changed_files': skipped,
              'before_free_bytes': before, 'after_free_bytes': shutil.disk_usage(ROOT).free}
    (AUDIT / 'latest_only_removed.json').write_text(json.dumps(result, indent=2) + '\n')
    paths = (AUDIT / 'commit_paths.txt').read_text().splitlines()
    paths += [x['path'] for x in removed if x['tracked'] and not x['path'].startswith('treasure_chest_20261113/')]
    (AUDIT / 'commit_paths.txt').write_text('\n'.join(dict.fromkeys(paths)) + '\n')
    print(json.dumps({'removed_files': len(removed), 'removed_GB': sum(x['bytes'] for x in removed) / 1e9,
                      'skipped': len(skipped), 'free_GB': result['after_free_bytes'] / 1e9}))

if __name__ == '__main__':
    (apply if len(sys.argv) > 1 and sys.argv[1] == 'apply' else plan)()
