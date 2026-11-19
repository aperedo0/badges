"""Temporary Shader AOV diagnostics for any Blender material, run in background.

The file on the command line is opened, changed only in memory, and never saved.
The target object gets a private copy of its mesh data and material, so the
production material is never touched, even in memory.

List the material's nodes and sockets first (to pick real signals):
  Blender -b SCENE.blend -P run_aovs.py -- CONFIG.json --list

Render the passes (the exit code flag makes a failure exit 1 instead of 0):
  Blender -b SCENE.blend --python-exit-code 1 -P run_aovs.py -- CONFIG.json

CONFIG.json:
{
  "object": "Object name",                      required
  "material": "Material name",                  optional, default first slot
  "scene": "Scene name",                        optional, default active scene
  "camera": "Camera object name",               optional, default scene camera
  "out": "/absolute/output/folder",             required
  "resolution": [1600, 800],                    optional
  "samples": 32,                                optional
  "border": [min_x, max_x, min_y, max_y],       optional crop, 0 to 1
  "signals": [
    {"name": "Rough", "kind": "VALUE", "node": "Principled BSDF", "socket": "Roughness"},
    {"name": "Color", "kind": "COLOR", "node": "Principled BSDF", "socket": "Base Color"},
    {"name": "Mask",  "kind": "VALUE", "node": "Mix", "socket": "Factor"},
    {"name": "Tex",   "kind": "COLOR", "node": "Image Texture", "output": "Color"},
    {"name": "TrueN", "kind": "COLOR", "geometry": "True Normal"}
  ]
}
"socket" reads an input socket (its link, or its constant when unlinked; an
unlinked Normal input reads the smooth shading normal it actually uses).
Diagnostics attach to the scene's first view layer.
"output" reads an output socket. "geometry" reads a Geometry node output. Add "display": "normal" to show any
direction vector as normal * 0.5 + 0.5 (automatic when the name says normal).

Writes to OUT: one folder of raw 32 bit EXR per signal, beauty.png, one PNG
preview per signal, sheet.png (beauty first, then signals in config order),
summary.md, signals.json, statistics.json and verification.json.
"""
import bpy, json, sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aov_tools import attach, configure_files, read_outputs, statistics

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
assert argv, 'Pass the config path after --'
cfg = json.loads(Path(argv[0]).read_text())
sc = bpy.data.scenes[cfg['scene']] if cfg.get('scene') else bpy.context.scene
obj = sc.objects[cfg['object']]
slots = [s for s in obj.material_slots if s.material]
assert slots, 'Object has no material'
mat_src = bpy.data.materials[cfg['material']] if cfg.get('material') else slots[0].material
assert mat_src.node_tree, 'Material has no node tree'
assert mat_src in [s.material for s in slots], f'{mat_src.name} is not on {obj.name}: {[s.material.name for s in slots]}'


_fresh = {}
def fresh_input(n, s):
    # A new node of the same type tells which constants are still Blender's defaults.
    if n.bl_idname not in _fresh:
        _fresh[n.bl_idname] = bpy.data.node_groups.new('defaults', 'ShaderNodeTree').nodes.new(n.bl_idname)
    return _fresh[n.bl_idname].inputs.get(s.identifier)


def inventory(mat):
    rows = []
    for n in mat.node_tree.nodes:
        row = dict(name=n.name, type=n.bl_idname, label=n.label, inputs=[], outputs=[])
        for s in n.inputs:
            if not s.enabled:
                continue
            item = dict(socket=s.name, linked=s.is_linked)
            if s.is_linked:
                l = s.links[0]
                item['from'] = f'{l.from_node.name} / {l.from_socket.name}'
            elif hasattr(s, 'default_value'):
                v = s.default_value
                f = fresh_input(n, s)
                if f is not None and hasattr(f, 'default_value') and str(list(v) if hasattr(v, '__len__') else v) == str(list(f.default_value) if hasattr(f.default_value, '__len__') else f.default_value):
                    continue
                item['value'] = [round(float(x), 5) for x in v] if hasattr(v, '__len__') else (round(float(v), 5) if isinstance(v, (int, float)) else str(v))
            row['inputs'].append(item)
        for s in n.outputs:
            if s.enabled and s.is_linked:
                row['outputs'].append(dict(socket=s.name, to=[f'{l.to_node.name} / {l.to_socket.name}' for l in s.links]))
        row['props'] = {k: getattr(n, k) for k in ('uv_map', 'attribute_name', 'operation', 'blend_type', 'data_type', 'space', 'interpolation', 'projection', 'extension') if getattr(n, k, '')}
        if n.bl_idname == 'ShaderNodeTexImage' and n.image:
            im = n.image
            row['image'] = dict(name=im.name, file=im.filepath, size=list(im.size), depth=im.depth,
                                float_buffer=im.is_float, colorspace=im.colorspace_settings.name, source=im.source)
        rows.append(row)
    return rows


if '--list' in argv:
    # One line per node keeps the inventory cheap to read.
    uvs = [u.name + (' (render)' if u.active_render else '') for u in getattr(obj.data, 'uv_layers', [])]
    print(f'AOV_INVENTORY material={mat_src.name!r} users={mat_src.users} slots={[s.material.name for s in slots]} uv={uvs} (unlinked inputs at default not shown)', flush=True)
    for row in inventory(mat_src):
        ins = '; '.join(f"{i['socket']}<-{i['from']}" if i['linked'] else f"{i['socket']}={i.get('value')}" for i in row['inputs'])
        outs = '; '.join(f"{o['socket']}->{', '.join(o['to'])}" for o in row['outputs'])
        img = (f" {row['props']}" if row['props'] else '') + (f" IMAGE {row['image']}" if 'image' in row else '')
        print(f"NODE {row['name']!r} [{row['type']}] IN: {ins} | OUT: {outs}{img}", flush=True)
    raise SystemExit(0)

out = Path(cfg['out'])
out.mkdir(parents=True, exist_ok=True)

# Private copies: diagnostics never reach the production mesh or material.
obj.data = obj.data.copy()
mat = mat_src.copy()
mat.name = 'Temporary AOV copy of ' + mat_src.name
for slot in obj.material_slots:
    if slot.material == mat_src:
        slot.material = mat
nt = mat.node_tree

specs = cfg['signals']
signals = []
notes_in = {}
geo = None
normal_names = {s['name'] for s in specs if s.get('display') == 'normal' or 'normal' in s['name'].lower()
                or s.get('geometry', '').endswith('Normal') or s.get('socket') == 'Normal'}
for s in specs:
    kind = s['kind'].upper()
    assert kind in ('VALUE', 'COLOR'), s
    if 'geometry' in s:
        if geo is None:
            geo = nt.nodes.new('ShaderNodeNewGeometry')
            geo.name = 'Diagnostic geometry'
        sock = geo.outputs[s['geometry']]
    else:
        node = nt.nodes[s['node']]
        sock = node.outputs[s['output']] if 'output' in s else node.inputs[s['socket']]
        if not sock.is_output and not sock.is_linked and sock.type == 'VECTOR' and 'Normal' in sock.name:
            # An unlinked normal input stores (0, 0, 0) but shades with the smooth normal.
            if geo is None:
                geo = nt.nodes.new('ShaderNodeNewGeometry')
                geo.name = 'Diagnostic geometry'
            sock = geo.outputs['Normal']
            notes_in[s['name']] = 'unlinked normal input: read the smooth shading normal it uses'
        if not sock.is_output and not sock.is_linked:
            kind = 'COLOR' if sock.type in ('RGBA', 'VECTOR') else 'VALUE'  # a constant keeps its own shape
        if kind == 'VALUE' and sock.type == 'RGBA':
            notes_in[s['name']] = 'color read as one gray value'
    signals.append((s['name'], kind, sock))
scope_node = nt.nodes.new('ShaderNodeValue')
scope_node.name = 'Diagnostic surface scope'
scope_node.outputs[0].default_value = 1.0
signals.append(('_scope', 'VALUE', scope_node.outputs[0]))

for v in sc.view_layers:  # render only the first used layer
    v.use = v == next(x for x in sc.view_layers if x.use)
records, aov_nodes = attach(sc, mat, signals)
names = [x[0] for x in signals]
writers = configure_files(sc, names, out)

r = sc.render
res = cfg.get('resolution')
if res:
    r.resolution_x, r.resolution_y = res
r.resolution_percentage = 100
if cfg.get('camera'):
    sc.camera = sc.objects[cfg['camera']]
b = cfg.get('border')
r.use_border = bool(b)
r.use_crop_to_border = bool(b)
if b:
    r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = b
if sc.render.engine == 'CYCLES':
    sc.cycles.samples = int(cfg.get('samples', 32))
    sc.cycles.seed = 17
r.filepath = str(out / 'beauty.png')
r.image_settings.file_format = 'PNG'
r.image_settings.color_mode = 'RGBA'
bpy.ops.render.render(write_still=True, scene=sc.name)

arrays = read_outputs(out, names)
stats, scope = statistics(arrays, '_scope')

# Classify every pass. A linked signal that comes out flat is the classic hidden
# bug (for example a 16 bit mask flattened by an 8 bit load).
verdicts = {}
for rec in records:
    name = rec['name']
    if name == '_scope':
        continue
    st = stats[name]
    flat = max(st['std']) < 1e-6
    linked = rec['connection'].startswith('Actual linked')
    if not flat:
        verdicts[name] = 'varies'
    elif not linked:
        verdicts[name] = 'constant input, expected'
    else:
        verdicts[name] = 'FLAT FROM A LINKED SIGNAL: check the source (expected for a Value or RGB node, or one flat face)'

# Zero control: a pass that reads all zero could be a real zero or a broken path.
# Feed the AOV output a known 1 in a tiny render to prove the path works.
zero = [n for n in names if n != '_scope' and max(abs(v) for v in stats[n]['max'] + stats[n]['min']) < 1e-7]
control = {}
if zero:
    saved = {}
    for n in zero:
        inp = aov_nodes[n].inputs['Color' if records[names.index(n)]['type'] == 'COLOR' else 'Value']
        saved[n] = [l.from_socket for l in inp.links]
        for l in list(inp.links):
            nt.links.remove(l)
        inp.default_value = (1, 1, 1, 1) if inp.type == 'RGBA' else 1.0
    cdir = out / 'zero_control'
    for n, w in writers.items():
        w.mute = n not in zero + ['_scope']
        w.directory = str(cdir / n)
    # Full resolution 16 px crop around one surface pixel: thin parts vanish at lower resolution.
    yy, xx = np.nonzero(scope)
    i = len(xx) // 2
    W, H = r.resolution_x, r.resolution_y
    cx = (r.border_min_x if b else 0) + (xx[i] + .5) / W
    cy = (r.border_min_y if b else 0) + (yy[i] + .5) / H
    r.use_border = r.use_crop_to_border = True
    r.border_min_x, r.border_max_x, r.border_min_y, r.border_max_y = cx - 8 / W, cx + 8 / W, cy - 8 / H, cy + 8 / H
    if sc.render.engine == 'CYCLES':
        sc.cycles.samples = 2
    r.filepath = str(cdir / 'beauty.png')
    bpy.ops.render.render(write_still=True, scene=sc.name)
    check = read_outputs(cdir, zero + ['_scope'])
    cscope = check['_scope'][:, :, 0] > .9999
    for n in zero:
        ok = cscope.sum() > 0 and float(np.max(abs(check[n][cscope] - 1))) < 1e-4
        control[n] = 'path verified, the zero is real' if ok else 'PATH BROKEN or no surface in crop'
        verdicts[n] = verdicts[n] + '; ' + control[n]

# Previews, written with Blender's own image API (no extra libraries needed).
def to_display(name, a):
    a = a.copy()
    note = ''
    if name in normal_names:
        a = a * .5 + .5
        note = 'shown as normal * 0.5 + 0.5'
    else:
        lo, hi = float(a[scope].min()), float(a[scope].max())
        if (lo < 0 or hi > 1) and hi - lo > 1e-6:
            a = (a - lo) / (hi - lo)
            note = f'stretched from {lo:.4g} to {hi:.4g}'
        kind = records[names.index(name)]['type']
        if kind == 'COLOR':
            a = np.clip(a, 0, 1)
            a = np.where(a <= .0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - .055)
    a[~scope] = .16
    return np.clip(a, 0, 1), note


def save_png(rgb, path):
    h, w = rgb.shape[:2]
    im = bpy.data.images.new(path.stem, w, h, alpha=True)
    px = np.ones((h, w, 4), np.float32)
    px[:, :, :3] = rgb
    im.pixels.foreach_set(px.ravel())
    im.filepath_raw = str(path)
    im.file_format = 'PNG'
    im.save()
    bpy.data.images.remove(im)


notes = {}
tiles = []
beauty = bpy.data.images.load(str(out / 'beauty.png'), check_existing=False)
bw, bh = beauty.size
bp = np.empty(bw * bh * 4, np.float32)
beauty.pixels.foreach_get(bp)
tiles.append(bp.reshape(bh, bw, 4)[:, :, :3])
bpy.data.images.remove(beauty)
for n in names:
    if n == '_scope':
        continue
    rgb, notes[n] = to_display(n, arrays[n])
    notes[n] = '; '.join(x for x in (notes_in.get(n, ''), notes[n]) if x)
    save_png(rgb, out / (n + '.png'))
    tiles.append(rgb)

h, w = tiles[0].shape[:2]
step = max(1, int(np.ceil(w / 480)))
tiles = [t[::step, ::step] for t in tiles if t.shape[:2] == (h, w)]
th, tw = tiles[0].shape[:2]
cols = 4
rows = int(np.ceil(len(tiles) / cols))
sheet = np.full((rows * (th + 8), cols * (tw + 8), 3), .1, np.float32)
for i, t in enumerate(tiles):
    y = (rows - 1 - i // cols) * (th + 8)
    x = (i % cols) * (tw + 8)
    sheet[y:y + th, x:x + tw] = t
save_png(sheet, out / 'sheet.png')

lines = ['# AOV summary', '', f'Material: {mat_src.name}. Object: {obj.name}. Surface pixels: {int(scope.sum())}.',
         'sheet.png reads left to right, top to bottom: beauty first, then the rows below in order.', '',
         '| # | Signal | Source | Min | Max | Mean | Verdict | Preview |', '|---|---|---|---|---|---|---|---|']
for i, rec in enumerate([x for x in records if x['name'] != '_scope'], 1):
    st = stats[rec['name']]
    src = f"{rec['source_node']} / {rec['source_socket']}" + ('' if rec['connection'].startswith('Actual linked') else ' (constant)')
    f = lambda v: f'{v[0]:.4g}' if max(v) - min(v) < 1e-9 else ', '.join(f'{x:.4g}' for x in v)
    lines.append(f"| {i} | {rec['name']} | {src} | {f(st['min'])} | {f(st['max'])} | {f(st['mean'])} | {verdicts[rec['name']]} | {notes[rec['name']]} |")
(out / 'summary.md').write_text('\n'.join(lines) + '\n')
(out / 'signals.json').write_text(json.dumps(records, indent=2))
(out / 'statistics.json').write_text(json.dumps(stats, indent=2))
(out / 'verification.json').write_text(json.dumps(dict(
    blender=bpy.app.version_string, material=mat_src.name, object=obj.name,
    surface_pixels=int(scope.sum()), verdicts=verdicts, zero_controls=control,
    production_material_untouched=True, file_saved=False), indent=2))
print('AOV_DONE ' + json.dumps(verdicts), flush=True)
