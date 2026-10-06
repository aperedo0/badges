"""Mobile export: the v1 reduction (unchanged) followed by the export rules (v2 rules 1 to 4
and, since v3, the rule 5 floor cut).

  Blender --background --factory-startup --python export_mobile.py -- \
      --root <output folder> --source <COPY of the master .blend> \
      --baked-usdz <full-resolution baked USDZ> --bakes <folder with the USDZ_*.png bakes> \
      [--inset-strength 0.4]

Only the lines marked v2 differ from badge_realitykit_handoff/scripts/export_mobile.py:
paths come from arguments, and the export at the end goes through
badge_mobile_rules.run(), which applies EXPORT_RULES.md and then exports with the same
USD settings and post-processing as v1.
"""
import bpy, json, math, traceback, re, sys, numpy as np
from pathlib import Path
from pxr import Usd,UsdGeom,UsdShade,UsdUtils,Sdf,Tf
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))  # v2
import badge_mobile_rules  # v2
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []  # v2
def arg(name,default=None):return ARGS[ARGS.index(name)+1] if name in ARGS else default  # v2
ROOT=Path(arg('--root','/Users/antonioperedo/Downloads/badge_realitykit_iron'))  # v3
SOURCE=Path(arg('--source',str(ROOT/'scenes/iron_medallion_master.blend')))  # v2
OLD_USDZ=arg('--baked-usdz',str(ROOT/'work/iron_baked.usdz'))  # v2
BAKES=Path(arg('--bakes',str(ROOT/'source/bakes')))  # v2
OUT=ROOT/'mobile/iron_badge_mobile.usdz'
for folder in ('reports','mobile/textures','scenes'):(ROOT/folder).mkdir(parents=True,exist_ok=True)  # v2
def status(stage,**extra):
    (ROOT/'reports/mobile_status.json').write_text(json.dumps(dict(stage=stage,**extra),indent=2))
def triangles(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)
def select(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True);bpy.context.view_layer.objects.active=obj
try:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene;scene.frame_set(360)
    rig=bpy.data.objects['Turntable | one slow 360 degree spin']
    original={o.name:o for o in rig.children_recursive if o.type=='MESH'}
    source_materials={m.name:m for o in original.values() for m in o.data.materials if m}
    for o in scene.objects:o.hide_render=True
    for name,obj in original.items():obj.name='SOURCE '+name
    stage=Usd.Stage.Open(OLD_USDZ)
    budgets={'Casing':28000,'Emblem':230,'Inner channel':3500,'Inner edge':2200,'Inset':3570,'Rim inner lip':2500}
    full_names={n.split(' | ')[0]:n for n in original}
    mesh_sources={next(k for k,n in full_names.items() if p.GetParent().GetName()==Tf.MakeValidIdentifier(n)):p for p in stage.Traverse() if p.IsA(UsdGeom.Mesh)}
    materials={}
    images={}
    texture_report=[]
    for stem in ('USDZ_Casing_base_color','USDZ_Casing_roughness','USDZ_Casing_normal',
                 'USDZ_Emblem_normal','USDZ_Inset_base_color','USDZ_Inset_normal'):
        file=BAKES/(stem+'.png')
        assert file.exists(),file
        img=bpy.data.images.load(str(file),check_existing=False)
        normal=stem.endswith('_normal')
        img.colorspace_settings.name='Non-Color' if normal or stem.endswith('_roughness') else 'sRGB'
        size=1024 if stem in ('USDZ_Emblem_normal','USDZ_Inset_normal') else 512
        img.scale(size,size)
        if normal and size==512:
            a=np.empty(size*size*4,dtype=np.float32);img.pixels.foreach_get(a)
            a=a.reshape((-1,4));v=a[:,:3]*2-1
            lengths=np.linalg.norm(v,axis=1);valid=lengths>1e-8
            v[valid]/=lengths[valid,None];a[:,:3]=(v+1)*.5
            img.pixels.foreach_set(a.ravel());img.update()
        path=ROOT/('mobile/textures/'+stem+'.png')
        img.filepath_raw=str(path);img.file_format='PNG';img.save()
        images[stem]=img
        texture_report.append(dict(file=str(path),width=size,height=size,normal_map=normal,
            convention='OpenGL tangent space: R=+X, G=+Y, B=+Z' if normal else None))
    def make_material(src,short):
        key=(src.name,short)
        if key in materials:return materials[key]
        mat=bpy.data.materials.new(src.name+' Mobile '+short);mat.use_nodes=True
        shader=mat.node_tree.nodes.get('Principled BSDF')
        old=next(n for n in src.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        for socket in old.inputs:
            target=shader.inputs.get(socket.name)
            if target and not socket.is_linked and hasattr(socket,'default_value'):
                try:target.default_value=socket.default_value
                except (TypeError,ValueError):pass
        channels={'Casing':('base_color','roughness','normal'),'Emblem':('normal',),'Inset':('base_color',)}.get(short,())
        for channel in channels:
            img=images['USDZ_'+short+'_'+channel]
            # A perfectly uniform image per casing material, preserving its own tone and roughness.
            if short=='Casing' and channel in ('base_color','roughness') and not src.name.startswith('Silver | circumferential'):
                img=img.copy()
                role='outer' if src.name.startswith('Outer edge') else 'back'
                img.name='USDZ_Casing_'+role+'_'+channel+'.png'
                col=(.105,.102,.094) if role=='outer' else (.055,.052,.048)
                if channel=='roughness':col=(.27,.27,.27) if role=='outer' else (.32,.32,.32)
                rgba=np.ones((512*512,4),dtype=np.float32);rgba[:,:3]=col
                img.pixels.foreach_set(rgba.ravel());img.update()
                img.filepath_raw=str(ROOT/'mobile/textures'/img.name);img.file_format='PNG';img.save();img.pack()
                images[img.name]=img
            tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img
            uv=mat.node_tree.nodes.new('ShaderNodeUVMap');uv.uv_map='USDZ_UV'
            mat.node_tree.links.new(uv.outputs['UV'],tex.inputs['Vector'])
            socket=tex.outputs['Color']
            target={'base_color':'Base Color','roughness':'Roughness','normal':'Normal'}[channel]
            if channel=='normal':
                decode=mat.node_tree.nodes.new('ShaderNodeNormalMap');decode.uv_map='USDZ_UV'
                mat.node_tree.links.new(socket,decode.inputs['Color']);socket=decode.outputs['Normal']
            mat.node_tree.links.new(socket,shader.inputs[target])
        mat['Source material']=src.name
        materials[key]=mat
        return mat
    result=[]
    low_objects=[]
    for short,target in budgets.items():
        name=full_names[short];prim=mesh_sources[short];usd=UsdGeom.Mesh(prim)
        pts=[tuple(p) for p in usd.GetPointsAttr().Get()]
        counts=list(usd.GetFaceVertexCountsAttr().Get())
        indices=list(usd.GetFaceVertexIndicesAttr().Get())
        assert all(n==3 for n in counts)
        faces=[indices[i:i+3] for i in range(0,len(indices),3)]
        mesh=bpy.data.meshes.new(name+' mobile geometry');mesh.from_pydata(pts,[],faces);mesh.update()
        obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
        low_objects.append(obj);obj.hide_render=False
        for poly in mesh.polygons:poly.use_smooth=True
        normals=usd.GetNormalsAttr().Get()
        attr=mesh.attributes.new('custom_normal','FLOAT_VECTOR','CORNER');attr.data.foreach_set('vector',np.asarray(normals,dtype=np.float32).ravel())
        for pv in UsdGeom.PrimvarsAPI(prim).GetPrimvars():
            if str(pv.GetTypeName())!='texCoord2f[]':continue
            values=pv.ComputeFlattened()
            if values is None:continue
            uv=mesh.uv_layers.new(name=str(pv.GetPrimvarName()))
            uv.data.foreach_set('uv',np.asarray(values,dtype=np.float32).ravel())
        if mesh.uv_layers.get('USDZ_UV'):
            mesh.uv_layers.active=mesh.uv_layers['USDZ_UV'];mesh.uv_layers.active.active_render=True
        src_slots=list(original[name].data.materials)
        for m in src_slots:mesh.materials.append(make_material(m,short))
        def mat_index(path):
            key=path.name
            for i,m in enumerate(src_slots):
                if key.startswith(Tf.MakeValidIdentifier(m.name)):return i
            raise AssertionError((name,key,[m.name for m in src_slots]))
        bound=UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
        base=mat_index(bound.GetPath())
        for p in mesh.polygons:p.material_index=base
        for subset in UsdGeom.Subset.GetAllGeomSubsets(UsdGeom.Imageable(prim)):
            idx=mat_index(UsdShade.MaterialBindingAPI(subset.GetPrim()).ComputeBoundMaterial()[0].GetPath())
            for poly in subset.GetIndicesAttr().Get():mesh.polygons[poly].material_index=idx
        high_mesh=mesh.copy()
        high=bpy.data.objects.new('NORMAL SOURCE '+short,high_mesh);scene.collection.objects.link(high)
        high.hide_render=True
        before=triangles(obj)
        select(obj)
        planar_count=before
        if False:  # frozen shipped enclosure already meets the budget; avoid non-reproducible decimation
            # Remove coplanar interior tessellation while protecting material, UV and normal boundaries.
            mod=obj.modifiers.new('Dissolve flat interiors','DECIMATE');mod.decimate_type='DISSOLVE'
            mod.angle_limit=math.radians(.15);mod.delimit={'NORMAL','MATERIAL','SEAM','UV'}
            bpy.ops.object.modifier_apply(modifier=mod.name)
            planar_count=triangles(obj)
            if planar_count>target:
                mod=obj.modifiers.new('Mobile triangle budget','DECIMATE');mod.decimate_type='COLLAPSE'
                mod.ratio=target/planar_count;mod.use_collapse_triangulate=True
                bpy.ops.object.modifier_apply(modifier=mod.name)
            transfer=obj.modifiers.new('Preserve source corner normals','DATA_TRANSFER')
            transfer.object=high;transfer.use_loop_data=True;transfer.data_types_loops={'CUSTOM_NORMAL'}
            transfer.loop_mapping='POLYINTERP_NEAREST'
            bpy.ops.object.modifier_apply(modifier=transfer.name)
        select(obj)
        tri=obj.modifiers.new('Mobile explicit triangles','TRIANGULATE')
        if hasattr(tri,'keep_custom_normals'):tri.keep_custom_normals=True
        bpy.ops.object.modifier_apply(modifier=tri.name)
        after=triangles(obj)
        bvh=BVHTree.FromPolygons([Vector(p) for p in pts],faces,all_triangles=True)
        samples=[]
        stride=max(1,len(obj.data.vertices)//5000)
        for v in list(obj.data.vertices)[::stride]:
            hit=bvh.find_nearest(v.co)
            if hit:samples.append(hit[3])
        # Face centers catch any planar shortcuts between retained vertices.
        for poly in list(obj.data.polygons)[::max(1,len(obj.data.polygons)//5000)]:
            hit=bvh.find_nearest(poly.center)
            if hit:samples.append(hit[3])
        result.append(dict(name=name,source_triangles=before,after_planar_dissolve=planar_count,
            target_triangles=target,triangles=after,vertices=len(obj.data.vertices),
            custom_normals=obj.data.has_custom_normals,emblem_geometry_unchanged=short=='Emblem',
            sampled_max_surface_deviation=float(max(samples)),sampled_p95_surface_deviation=float(np.percentile(samples,95)),
            material_slots=[m.name for m in obj.data.materials]))
        status('decimating',completed=short,triangles=after)
    total=sum(x['triangles'] for x in result)
    assert 37000<=total<=42000,total
    collection=bpy.data.collections.new('Mobile badge only');scene.collection.children.link(collection)
    for obj in low_objects:
        for c in list(obj.users_collection):c.objects.unlink(obj)
        collection.objects.link(obj)
    for obj in list(scene.objects):
        if obj not in low_objects:
            bpy.data.objects.remove(obj,do_unlink=True)
    scene.camera=None
    select(low_objects[0])
    for obj in low_objects:obj.select_set(True)
    for img in images.values():img.pack()
    scene['Source file']=str(SOURCE)
    scene['Model orientation']='Y up, front +Z, native diameter 6.03 units; preserve scale or normalize in app.'
    # v2: keep the reduced scene before the rules (the v1 mobile .blend), then apply the rules and export.
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scenes/iron_badge_mobile_reduced.blend'),check_existing=False)
    config=dict(badge_mobile_rules.SILVER_CONFIG)  # v2
    if arg('--inset-strength'):config['normal_map_strength']={'Inset':float(arg('--inset-strength'))}  # v2
    rules=badge_mobile_rules.run(None,OUT,ROOT/'mobile/textures',apply=True,config=config,
        save_blend=ROOT/'scenes/iron_badge_mobile.blend')  # v2
    output_stage=Usd.Stage.Open(str(OUT))  # v2: read back for the name mapping report
    usd_meshes=[p for p in output_stage.Traverse() if p.IsA(UsdGeom.Mesh)]
    assert len(usd_meshes)==6
    mapping=[]
    for p in usd_meshes:
        for row in result:
            if p.GetParent().GetName()==Tf.MakeValidIdentifier(row['name']):
                n=sum(int(x)-2 for x in UsdGeom.Mesh(p).GetFaceVertexCountsAttr().Get())
                assert n==row['triangles'],(n,row)
                mapping.append(dict(source_name=row['name'],usd_mesh_path=str(p.GetPath()),triangles=n))
    assert len(mapping)==6
    texture_report=list(rules['textures'].values())  # v2: only the textures the file still uses
    for leftover in (ROOT/'mobile/textures').glob('USDZ_*.png'):  # v2: bakes the rules dropped
        if leftover.name not in rules['textures']:leftover.unlink()
    report=dict(source_blend=str(SOURCE),baked_uv_source=OLD_USDZ,meshes=result,smoothness_rules=rules,
        total_triangles=total,source_total_triangles=sum(x['source_triangles'] for x in result),
        file=str(OUT),file_bytes=OUT.stat().st_size,texture_files=texture_report,
        usd_name_mapping=mapping,normal_convention='OpenGL tangent space, +X red, +Y green, +Z blue. No green-channel inversion.',
        source_original_untouched=True)
    (ROOT/'reports/mobile_model.json').write_text(json.dumps(report,indent=2))
    status('complete',triangles=total,bytes=OUT.stat().st_size)
except Exception:
    status('error',traceback=traceback.format_exc())
    raise

