from pathlib import Path
P=Path(__file__).resolve().parent
# Reuse the same framing and lighting functions used for all draft comparisons.
code=(P/'render_batch.py').read_text().split('jobs=')[0].replace("sc=bpy.data.scenes['Wood surface comparison']","sc=bpy.data.scenes['Test plank master']")
exec(compile(code,'shared_render_setup','exec'))
master=sc.objects['Master Chest Body Envelope'];source=bpy.data.scenes['Chest Complete Form Phase 1'];a=source.objects['Chest Body Envelope'].copy();a.parent=None;a.matrix_world=source.objects['Chest Body Envelope'].matrix_world.copy();a.name='Temporary baseline body';sc.collection.objects.link(a);a.hide_render=True
# One isolated temporary material per surrounding surface class, used only for context.
def mat(name,color,metal,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough;return m
iron=mat('Temporary context iron',(.065,.048,.038),1,.33);brass=mat('Temporary context brass',(.57,.29,.072),1,.27);wood=mat('Temporary context quiet wood',(.14,.046,.014),0,.64);clay=mat('Relief diagnostic clay',(.28,.28,.28),0,.76)
context=[]
for o in sc.objects:
 if o.type!='MESH' or o in [master,a] or o.name=='Lab Development floor':continue
 o.data=o.data.copy();old=list(o.data.materials)
 name=o.name
 m=wood if 'Envelope' in name else brass if any(t in name for t in ['Rivet','Fastener','Dome','Diamond','Lock Plate','Lock Border','Hasp','Ring Handle','Rolled Handle']) and 'Seat' not in name else iron
 o.data.materials.clear();o.data.materials.append(m)
 for f in o.data.polygons:f.material_index=0
 context.append((o,old))
body_old=list(master.data.materials)
def materials(mode):
 for o,old in context:
  o.data.materials.clear()
  for m in (old if mode!='context' else [wood if 'Envelope' in o.name else brass if any(t in o.name for t in ['Rivet','Fastener','Dome','Diamond','Lock Plate','Lock Border','Hasp','Ring Handle','Rolled Handle']) and 'Seat' not in o.name else iron]):o.data.materials.append(m)
 for i,m in enumerate(body_old):master.data.materials[i]=clay if mode=='clay' else wood if mode=='context' and 'Sample45' not in m.name and m.name!='Wood Lab H' else m
# Restrict temporary surrounding wood to a plain contextual color. No approved system transfer.
jobs=[('baseline_neutral_close','baseline','neutral','close','neutral'),('master_neutral_close','master','neutral','close','neutral'),('baseline_cinema_close','baseline','cinema','close','neutral'),('master_cinema_close','master','cinema','close','neutral'),('master_cinema_full','master','cinema','full','neutral'),('master_context_full','master','cinema','full','context'),('master_context_close','master','cinema','close','context'),('master_clay_graze','master','graze','close','clay'),('master_opposed_close','master','opposed','close','neutral')]
done=[]
for name,which,light,view,material in jobs:
 out=P/'final_renders'/(name+'.png');out.parent.mkdir(exist_ok=True)
 if out.exists():continue
 master.hide_render=which=='baseline';a.hide_render=which!='baseline';materials(material);lighting(light);frame(view);sc.render.resolution_x=1600 if view!='full' else 1400;sc.render.resolution_y=1184 if view!='full' else 1400;sc.cycles.samples=128 if material!='clay' else 64;sc.render.resolution_percentage=100;sc.render.filepath=str(out);st=time.time();bpy.ops.render.render(write_still=True);done.append([name,round(time.time()-st,1)]);(P/'final_render_progress.json').write_text(json.dumps(done,indent=2));print('FINAL',done[-1],flush=True)
