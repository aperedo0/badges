"""Download free CC0 textures and HDRIs into a cache and record where they came from.

Standard library only, so any Python 3 works (no Pillow or numpy needed).

Look before downloading (prints maps and sizes; --preview saves the preview):
  python3 fetch_free_asset.py polyhaven rough_wood --cache DIR --preview
  python3 fetch_free_asset.py ambientcg Metal003 --cache DIR --preview
Download chosen maps at one resolution:
  python3 fetch_free_asset.py polyhaven rough_wood --cache DIR --res 2k --maps Diffuse,Rough,nor_gl,Displacement
  python3 fetch_free_asset.py polyhaven studio_small_03 --cache DIR --res 1k --maps hdri
  python3 fetch_free_asset.py ambientcg Metal003 --cache DIR --res 1K --fmt PNG
Any other free site with a direct file link (cgbookcase, TextureCan, or 3dtextures.me
through Google Drive file links, which need --save-as because they carry no file name):
  python3 fetch_free_asset.py url https://example/file.zip --cache DIR --name battered_metal_02 \
      --page https://www.cgbookcase.com/textures/battered-metal-02 --license CC0
  python3 fetch_free_asset.py url 'https://drive.google.com/uc?export=download&id=ID' --cache DIR \
      --name metal_hammered_003 --save-as roughness.jpg --page PAGE --license CC0

Every download goes to DIR/<source>_<asset>/, zips are unpacked (macOS ._ files
skipped), and DIR/SOURCES.json gains one entry with page, license, file URLs and
sha256 hashes (or the file named by --record). Files already in the cache are
never downloaded again. ambientCG listing uses its public v2 API.
"""
import argparse, datetime, hashlib, json, sys, urllib.request, zipfile
from pathlib import Path

AGENT = {'User-Agent': 'free-asset-sources-skill/1.0'}


def fetch(url, dest=None):
    if dest is not None and dest.exists():
        return dest.read_bytes()
    req = urllib.request.Request(url, headers=AGENT)
    with urllib.request.urlopen(req, timeout=180) as r:
        if r.headers.get_content_type() == 'text/html':
            raise SystemExit(f'{url} is a web page, not a file. Use the direct file link.')
        data = r.read()
    if dest is not None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return data


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def unpack(zpath, folder):
    with zipfile.ZipFile(zpath) as z:
        names = [n for n in z.namelist() if not Path(n).name.startswith('._') and not n.endswith('/') and '__MACOSX' not in n]
        for n in names:
            target = folder / Path(n).name
            if not target.exists():
                target.write_bytes(z.read(n))
    return [Path(n).name for n in names]


def record(cache, entry):
    path = RECORD or cache / 'SOURCES.json'
    items = json.loads(path.read_text()) if path.exists() else []
    if not isinstance(items, list):
        raise SystemExit(f'{path} is not a list; pass a new --record file.')
    old = next((i for i in items if isinstance(i, dict) and i.get('key') == entry['key']), None)
    if old:  # later calls add maps and keep the earlier note
        entry['files'] = {**(old['files'] if isinstance(old.get('files'), dict) else {}), **entry['files']}
        entry['note'] = entry['note'] or old.get('note', '')
    path.parent.mkdir(parents=True, exist_ok=True)
    items = [i for i in items if i.get('key') != entry['key']] + [entry]
    path.write_text(json.dumps(items, indent=2))
    print('RECORDED', entry['key'], '->', path)


def polyhaven(a):
    info = json.loads(fetch('https://api.polyhaven.com/info/' + a.asset))
    files = json.loads(fetch('https://api.polyhaven.com/files/' + a.asset))
    kind = {0: 'hdri', 1: 'texture', 2: 'model'}.get(info.get('type'), 'unknown')
    page = 'https://polyhaven.com/a/' + a.asset
    preview = f'https://cdn.polyhaven.com/asset_img/primary/{a.asset}.png?width=700'
    maps = {k: v for k, v in files.items() if isinstance(v, dict) and all(isinstance(x, dict) for x in v.values())}
    folder = a.cache / ('polyhaven_' + a.asset)
    if not a.maps:
        print(f"{info.get('name')} ({kind}) {page}\npreview: {preview}")
        if a.preview:
            fetch(preview, folder / 'preview.png')
            print('PREVIEW', folder / 'preview.png')
        for name, by_res in maps.items():
            sizes = ', '.join(f"{r}: " + '/'.join(f"{fmt} {f.get('size', 0) / 1e6:.1f}MB" for fmt, f in fm.items() if isinstance(f, dict) and 'url' in f)
                              for r, fm in by_res.items())
            print(f'  {name}: {sizes}')
        print('Look at the preview (--preview saves it), then add --res and --maps to download.')
        return
    if not a.res:
        raise SystemExit('Add --res (for example 1k or 2k) with --maps.')
    a.res = a.res.lower()
    got = {}
    if a.preview:
        fetch(preview, folder / 'preview.png')
        got['preview.png'] = preview
    wanted = a.maps.split(',')
    bad = [m for m in wanted if a.res not in maps.get(m, {})]
    if bad:
        raise SystemExit(f'No {", ".join(bad)} at {a.res}. Run without --maps to list what exists.')
    for m in wanted:
        by_fmt = maps[m][a.res]
        fmt = a.fmt.lower() if a.fmt and a.fmt.lower() in by_fmt else next((f for f in ('png', 'jpg', 'exr', 'hdr') if f in by_fmt), next(iter(by_fmt)))
        url = by_fmt[fmt]['url']
        fetch(url, folder / url.rsplit('/', 1)[1])
        got[url.rsplit('/', 1)[1]] = url
        print('GOT', m, url)
    record(a.cache, dict(key='polyhaven_' + a.asset, asset=info.get('name'), type=kind, source='Poly Haven', page=page,
                         authors=list(info.get('authors', {}).keys()), license='CC0 1.0', license_url='https://polyhaven.com/license',
                         api='https://polyhaven.com/our-api', resolution=a.res, note=a.note,
                         files={n: dict(url=u, sha256=sha(folder / n)) for n, u in got.items()},
                         date=datetime.date.today().isoformat()))


def ambientcg(a):
    res, fmt = (a.res or '1K').upper(), (a.fmt or 'PNG').upper()
    name = f'{a.asset}_{res}-{fmt}.zip'
    url = 'https://ambientcg.com/get?file=' + name
    page = 'https://ambientcg.com/view?id=' + a.asset
    folder = a.cache / ('ambientcg_' + a.asset)
    if not a.res:
        found = json.loads(fetch(f'https://ambientcg.com/api/v2/full_json?id={a.asset}&include=downloadData,previewData'))['foundAssets']
        if not found:
            raise SystemExit('No ambientCG asset ' + a.asset)
        x = found[0]
        zips = x['downloadFolders']['default']['downloadFiletypeCategories']['zip']['downloads']
        print(f"{x['displayName']} {page}\nmaps: {', '.join(x.get('maps', []))}")
        print('  ' + ', '.join(f"{d['attribute']} {d['size'] / 1e6:.1f}MB" for d in zips))
        if a.preview:
            fetch(x['previewImage']['512-PNG'], folder / 'preview.png')
            print('PREVIEW', folder / 'preview.png')
        return
    z = folder / name
    fetch(url, z)
    names = unpack(z, folder)
    print('GOT', url, '->', ', '.join(names))
    record(a.cache, dict(key='ambientcg_' + a.asset, asset=a.asset, source='ambientCG', page=page, download=url,
                         license='CC0 1.0', license_url='https://docs.ambientcg.com/license/',
                         files={name: dict(url=url, sha256=sha(z), unpacked=names)}, note=a.note, date=datetime.date.today().isoformat()))


def direct(a):
    if not (a.name and a.page and a.license):
        raise SystemExit('url needs --name, --page and --license')
    folder = a.cache / ('url_' + a.name)
    fname = a.save_as or a.asset.split('?')[0].rstrip('/').rsplit('/', 1)[-1]
    if '.' not in fname:
        raise SystemExit('This link has no file name; add --save-as NAME.ext')
    dest = folder / fname
    fetch(a.asset, dest)
    names = unpack(dest, folder) if zipfile.is_zipfile(dest) else [fname]
    print('GOT', a.asset, '->', ', '.join(names))
    record(a.cache, dict(key='url_' + a.name, asset=a.name, page=a.page, license=a.license,
                         files={fname: dict(url=a.asset, sha256=sha(dest), unpacked=names)}, note=a.note,
                         date=datetime.date.today().isoformat()))


p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('source', choices=['polyhaven', 'ambientcg', 'url'])
p.add_argument('asset', help='Poly Haven id, ambientCG id, or a direct URL')
p.add_argument('--cache', type=Path, required=True)
p.add_argument('--res', help='polyhaven: 1k, 2k, 4k. ambientcg: 1K, 2K, 4K')
p.add_argument('--maps', help='polyhaven map names from the listing, comma separated (hdri for an HDRI)')
p.add_argument('--fmt', help='preferred format: png, jpg, exr, hdr (ambientcg: PNG or JPG)')
p.add_argument('--preview', action='store_true', help='also save the preview image')
p.add_argument('--name'); p.add_argument('--page'); p.add_argument('--license')
p.add_argument('--save-as', help='url: file name for links without one (Google Drive)')
p.add_argument('--note', default='', help='what this asset is used for, or which channels are ignored')
p.add_argument('--record', type=Path, help='where SOURCES.json goes (default inside the cache); put it outside an ignored cache to keep it in Git')
a = p.parse_args()
RECORD = a.record
a.cache.mkdir(parents=True, exist_ok=True)
{'polyhaven': polyhaven, 'ambientcg': ambientcg, 'url': direct}[a.source](a)
