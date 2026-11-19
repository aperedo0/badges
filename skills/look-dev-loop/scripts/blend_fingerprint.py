"""Prove a Blender checkpoint: fingerprint a file, then compare a later save against it.

Snapshot (background, opens FILE):
  Blender -b --python-exit-code 1 -P blend_fingerprint.py -- snapshot FILE.blend OUT.json
Compare a candidate against a snapshot; objects or materials named after --allow
may differ (this round's work), everything else must match exactly:
  Blender -b --python-exit-code 1 -P blend_fingerprint.py -- compare BASE.json CAND.blend [--allow NAME ...]
Snapshot the owner's live scene through the Blender connection, without saving it:
  import runpy, json; ns = runpy.run_path('/abs/path/blend_fingerprint.py')
  json.dump(ns['snapshot'](), open('/abs/out.json', 'w'))

Covers: every object's type, parent, transform, modifiers and material slots;
mesh positions, polygons and every UV layer; every material, world and node group
graph (nodes, settings, unlinked values, links); lights; cameras; scene render and
color management settings; images (missing or unpacked files always fail).
Prints one PASS or FAIL line, then at most 40 differences; writes all of them to
CAND.fingerprint_diff.json. Exit code 1 on FAIL (with --python-exit-code 1).
"""
import bpy, hashlib, json, os, sys
import numpy as np

SKIP = {'rna_type', 'name', 'label', 'location', 'width', 'height', 'dimensions', 'select', 'show_options',
        'show_preview', 'hide', 'parent', 'color', 'use_custom_color', 'show_texture', 'inputs', 'outputs',
        'internal_links', 'type', 'bl_idname', 'bl_label', 'bl_description', 'bl_icon', 'bl_static_type',
        'bl_width_default', 'bl_width_min', 'bl_width_max', 'bl_height_default', 'bl_height_min', 'bl_height_max',
        'width_hidden', 'is_active_output', 'warning_propagation', 'location_absolute', 'color_tag'}


def h(*arrays):
    d = hashlib.sha256()
    for a in arrays:
        d.update(np.ascontiguousarray(a).tobytes())
    return d.hexdigest()[:16]


def r(v, n=6):
    try:
        return [round(float(x), n) for x in v]
    except TypeError:
        return round(float(v), n) if isinstance(v, (int, float)) else v


def node_settings(n):
    out = {}
    for p in n.bl_rna.properties:
        k = p.identifier
        if k in SKIP or k.startswith('bl_'):
            continue
        try:
            v = getattr(n, k)
        except Exception:
            continue
        if p.type == 'POINTER':
            out[k] = getattr(v, 'name', None) if v is not None else None
        elif p.type == 'COLLECTION':
            continue
        elif p.type == 'ENUM' and p.is_enum_flag:
            out[k] = sorted(v)
        elif p.type in ('FLOAT', 'INT'):
            out[k] = r(v)
        else:
            out[k] = v if isinstance(v, (bool, str, int, float)) or v is None else str(v)
    if getattr(n, 'color_ramp', None):
        out['ramp'] = [(round(e.position, 6), r(e.color)) for e in n.color_ramp.elements] + [n.color_ramp.interpolation]
    if getattr(n, 'mapping', None) and hasattr(n.mapping, 'curves'):
        out['curves'] = [[r(p.location) for p in c.points] for c in n.mapping.curves]
    return out


def graph(tree):
    if tree is None:
        return None
    nodes = {}
    for n in tree.nodes:
        ins = {}
        for i, s in enumerate(n.inputs):
            if not s.is_linked and hasattr(s, 'default_value'):
                v = s.default_value
                ins[f'{i}:{s.identifier}'] = r(v) if not isinstance(v, str) else v
        e = dict(type=n.bl_idname, mute=n.mute, settings=node_settings(n), inputs=ins)
        nodes[n.name] = hashlib.sha256(json.dumps(e, sort_keys=True, default=str).encode()).hexdigest()[:12]
    links = sorted(f'{l.from_node.name}/{l.from_socket.identifier}>{l.to_node.name}/{l.to_socket.identifier}'
                   for l in tree.links if l.is_valid and not l.is_muted)
    return dict(nodes=nodes, links=hashlib.sha256('|'.join(links).encode()).hexdigest()[:12], link_count=len(links))


def mesh_print(me):
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co)
    lv = np.empty(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
    tot = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('loop_total', tot)
    mi = np.empty(len(me.polygons), np.int32); me.polygons.foreach_get('material_index', mi)
    uvs = {}
    for uv in me.uv_layers:
        a = np.empty(len(uv.data) * 2, np.float32); uv.data.foreach_get('uv', a); uvs[uv.name] = h(a)
    return dict(vertices=len(me.vertices), polygons=len(me.polygons), positions=h(co),
                topology=h(lv, tot), material_index=h(mi), uv=uvs)


def snapshot():
    s = dict(objects={}, materials={}, worlds={}, node_groups={}, lights={}, cameras={}, scenes={}, images={})
    for o in bpy.data.objects:
        e = dict(type=o.type, parent=o.parent.name if o.parent else None, matrix=[r(row) for row in o.matrix_world],
                 hide_render=o.hide_render, modifiers=[(m.name, m.type, m.show_render) for m in o.modifiers],
                 slots=[(sl.link, sl.material.name if sl.material else None) for sl in o.material_slots])
        if o.type == 'MESH':
            e['mesh'] = mesh_print(o.data)
        s['objects'][o.name] = e
    for m in bpy.data.materials:
        s['materials'][m.name] = dict(graph=graph(m.node_tree), blend=getattr(m, 'surface_render_method', None))
    for w in bpy.data.worlds:
        s['worlds'][w.name] = graph(w.node_tree)
    for g in bpy.data.node_groups:
        s['node_groups'][g.name] = graph(g)
    for l in bpy.data.lights:
        s['lights'][l.name] = dict(type=l.type, energy=r(l.energy), color=r(l.color),
                                   size=r(getattr(l, 'size', 0)), size_y=r(getattr(l, 'size_y', 0)),
                                   shape=getattr(l, 'shape', None), spot=r(getattr(l, 'spot_size', 0)))
    for c in bpy.data.cameras:
        s['cameras'][c.name] = dict(type=c.type, lens=r(c.lens), ortho=r(c.ortho_scale), sensor=r(c.sensor_width),
                                    shift=r((c.shift_x, c.shift_y)), clip=r((c.clip_start, c.clip_end)))
    for sc in bpy.data.scenes:
        rs, vs = sc.render, sc.view_settings
        s['scenes'][sc.name] = dict(engine=rs.engine, camera=sc.camera.name if sc.camera else None,
                                    world=sc.world.name if sc.world else None, frame=sc.frame_current,
                                    resolution=(rs.resolution_x, rs.resolution_y, rs.resolution_percentage),
                                    view=(vs.view_transform, vs.look, r(vs.exposure), r(vs.gamma)),
                                    display=sc.display_settings.display_device,
                                    objects=sorted(o.name for o in sc.objects))
    for im in bpy.data.images:
        if im.source in ('VIEWER',) or im.type in ('RENDER_RESULT', 'COMPOSITING'):
            continue
        path = bpy.path.abspath(im.filepath) if im.filepath else ''
        missing = im.source == 'FILE' and not im.packed_file and not (path and os.path.exists(path))
        s['images'][im.name] = dict(source=im.source, packed=bool(im.packed_file), file=im.filepath,
                                    size=list(im.size), missing=missing,
                                    data=hashlib.sha256(bytes(im.packed_file.data)).hexdigest()[:16] if im.packed_file else None)
    return s


def diff(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            p = f'{path}/{k}'
            if k not in a:
                out.append((p, 'added'))
            elif k not in b:
                out.append((p, 'removed'))
            else:
                out += diff(a[k], b[k], p)
        return out
    return [] if a == b else [(path, f'{json.dumps(a, default=str)[:60]} -> {json.dumps(b, default=str)[:60]}')]


if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:]
    mode = argv[0]
    if mode == 'snapshot':
        bpy.ops.wm.open_mainfile(filepath=argv[1])
        with open(argv[2], 'w') as f:
            json.dump(snapshot(), f, indent=1, default=str)
        print('SNAPSHOT', argv[2], flush=True)
    elif mode == 'compare':
        base = json.load(open(argv[1]))
        cand = argv[2]
        allow = set(argv[argv.index('--allow') + 1:]) if '--allow' in argv else set()
        bpy.ops.wm.open_mainfile(filepath=cand)
        now = json.loads(json.dumps(snapshot(), default=str))
        found = diff(base, now)
        allowed = [d for d in found if len(d[0].split('/')) > 2 and d[0].split('/')[2] in allow]
        bad = [d for d in found if d not in allowed]
        bad += [(f'/images/{k}', 'MISSING FILE') for k, v in now['images'].items() if v['missing']]
        bad += [(f'/images/{k}', 'not packed') for k, v in now['images'].items()
                if v['source'] == 'FILE' and not v['packed'] and not v['missing'] and '--allow-unpacked' not in argv]
        out = os.path.splitext(cand)[0] + '.fingerprint_diff.json'
        with open(out, 'w') as f:
            json.dump(dict(failures=bad, allowed=allowed), f, indent=1)
        print(('PASS' if not bad else 'FAIL') + f' {len(bad)} differences, {len(allowed)} allowed; details {out}', flush=True)
        for p, what in bad[:40]:
            print('  ', p, what, flush=True)
        if bad:
            raise SystemExit(1)
    else:
        raise SystemExit('mode must be snapshot or compare')
