"""Package reviewed copies without changing production assets."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parent;rows=json.loads((ROOT/'manifest.json').read_text());res=json.loads((ROOT/'results.json').read_text());exports=[];preservation=[]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for row in rows:
 d=res[row['key']];changed=d['status']=='validated_candidate';base=ROOT/'badges'/row['slug'];c=base/'candidate01'
 assert sha(base/'baseline/model.usdz')==row['source_sha256']
 for alias in row['aliases']:
  expected=d['output_sha256'] if changed and alias['origin']=='preview' else row['source_sha256'];actual=sha(alias['path']);assert actual==expected,alias['path'];preservation.append(dict(path=alias['path'],origin=alias['origin'],sha256=actual,expected=expected))
 if not changed:continue
 assert sha(c/'model.usdz')==d['output_sha256']
 review=c/'review';loaded=json.loads((review/'loaded_model.json').read_text());assert loaded['sha256']==d['output_sha256'] and loaded['capture_version']==2
 assert json.loads((base/'baseline/loaded_model.json').read_text())['sha256']==row['source_sha256']
 alignment=json.loads((review/'pose_alignment.json').read_text());assert len(alignment)==6 and all(abs(v['actual_header_y']-v['target_header_y'])<=1.5 for v in alignment.values())
 assert (review/'full_turn.mp4').stat().st_size>10000;assert (c/'checkpoint_validation.json').exists()
 name=('original_iron' if row['key']=='iron' else row['slug'])+'_badge_mobile.usdz';mobile=base/'mobile';previous=mobile/'previous';previous.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/'baseline/model.usdz',previous/name);shutil.copyfile(c/'model.usdz',mobile/name)
 flat=ROOT/'mobile';flat.mkdir(exist_ok=True);shutil.copyfile(c/'model.usdz',flat/name)
 runtime=[]
 if (c/'runtime_launch.json').exists():
  info=json.loads((c/'runtime_launch.json').read_text());log=Path(info['logs']['runtimeLogPath'])
  runtime=[line for line in log.read_text(errors='replace').splitlines() if 'Badge gem attached: CrestGem_' in line]
  if runtime:(c/'runtime_attachment.txt').write_text('\n'.join(runtime)+'\n')
 expected_gems=sum('CrestGem_' in s for s in row['material_names'])
 expected_gem_meshes=sum(n for s,n in row['material_names'].items() if s.startswith('CrestGem_'))
 if expected_gem_meshes:
  assert len([s for s in runtime if 'mirror=false' in s])==expected_gem_meshes,(row['title'],runtime)
  assert len([s for s in runtime if 'mirror=true' in s])==expected_gem_meshes
 d.update(native_review_complete=True,editable_checkpoint_verified=True,final=str(mobile/name),flat_export=str(flat/name),optical_gem_attachment_count=expected_gem_meshes)
 note=f"Combined compatible surfaces from {d['before']['meshes']} to {d['after']['meshes']} meshes and {d['before']['sections']} to {d['after']['sections']} material sections.\nAll triangles, normals, UVs, materials, textures and protected meshes are preserved; reviewed against the original in six native poses and a complete turn.\n"
 (c/'NOTES.md').write_text(note);(base/'REPORT.md').write_text(note+'\n[Final model](mobile/'+name+') · [Before and after](candidate01/review/all_sides_comparison.png) · [Four times details](candidate01/review/difference_details_4x.png) · [Rotation](candidate01/review/full_turn.mp4) · [Editable Blender file](candidate01/source/model.blend)\n')
 exports.append(dict(key=row['key'],title=row['title'],filename=name,sha256=d['output_sha256'],file=str(flat/name),production_targets=[a['path'] for a in row['aliases'] if a['origin']=='production']))
plan=[]
for row in rows:
 d=res[row['key']]
 if d['status']!='validated_candidate':continue
 for a in row['aliases']:plan.append(dict(key=row['key'],title=row['title'],origin=a['origin'],target=a['path'],source=d['flat_export'],expected_original_sha256=row['source_sha256'],replacement_sha256=d['output_sha256']))
(ROOT/'integration_plan.json').write_text(json.dumps(plan,indent=2)+'\n')
(ROOT/'results.json').write_text(json.dumps(res,indent=2)+'\n');(ROOT/'preservation_validation.json').write_text(json.dumps(preservation,indent=2)+'\n');(ROOT/'exports.json').write_text(json.dumps(exports,indent=2)+'\n')
changed=[r for r in rows if res[r['key']]['status']=='validated_candidate'];before={k:sum(res[r['key']]['before'][k] for r in changed) for k in ['meshes','sections','triangles']};after={k:sum(res[r['key']]['after'][k] for r in changed) for k in ['meshes','sections','triangles']};sizes=[sum(res[r['key']][f'bytes_{part}'] for r in changed) for part in ['before','after']]
text=f"""The 28 changed badges keep their approved appearance with fewer separate drawing parts. Meshes decrease from {before['meshes']} to {after['meshes']}, and material sections from {before['sections']} to {after['sections']}. The same {before['triangles']:,} triangles remain. Combined model size changes from {sizes[0]/1000000:.2f} MB to {sizes[1]/1000000:.2f} MB.

All 35 distinct current gallery models were inventoried against the private preview and production assets. Six existing models remain byte identical. Five were already compact: Crimson Shield, Diamond, Mountain Crest, Platinum and Winged Sword. Steel already has two meshes; its trial changed native highlights, so it was rejected and its approved original was retained. Astral Navigator retains its approved 23 mesh final. Every other model now has at most 12 meshes.

The reviewed exports are in [mobile](mobile). Each changed badge also has its own mobile folder, a previous copy, a complete editable Blender checkpoint, validation, six native comparison poses, enlarged details and a full rotation recording. The original approved sources and all production assets remain preserved. The private Badge Studio Preview was updated with the optimized models.

The cleanup combines compatible material batches. It preserves every oriented triangle corner position, normal, named UV set and other vertex attributes, plus its effective material. Material graphs and texture file bytes are unchanged. The coin casing and inset prims are copied intact with their runtime names. Optical gems remain separate closed meshes; runtime logs confirm all 19 affected optical stones and their reflections received their gem shaders. No shared lighting, material tuning, placement or shader code changes were needed.

The originals were compared in the actual preview at matching scroll positions, with resting front, early turn, both sides, back and a slow complete turn. Complete pose pairs and focused rendering differences were inspected, including enlarged local differences. Full four times comparison images are retained for every pose. The Blender working copies were inspected live; their final standalone files were checked in an isolated background process to verify packed image bytes and restore unique canonical names. Original source camera conventions were retained. Incorrect picker captures were rejected and replaced after verifying the displayed badge title; gesture positions were measured to avoid comparing different angles.

This is object and material batching, preserving existing approved artwork rather than rebuilding its mockup. Existing polygon counts and texture resolutions deliberately remain unchanged. Some individual files grow slightly because their array layout changes, although the combined size falls. Emerald Trophy remains above 5 MB and Sapphire Stairway slightly above 5 MB to retain their approved detail. This reduces file and object overhead; actual iPhone frame rates and the unchanged optical rendering cost were not benchmarked.

Production integration is an asset replacement only. [exports.json](exports.json) maps each reviewed file and hash to its production target. There are 27 production replacements and one private only Original Iron variant. Do not substitute Original Iron for the production Iron badge, which is Crimson Shield. Existing placement and runtime material handling stay as they are. The separate simulator preview is installed; production integration has not been performed by this task.

Badge | Meshes before | Meshes after | Sections before | Sections after | Result
:-- | --: | --: | --: | --: | :--
"""
for row in sorted(rows,key=lambda r:r['title']):
 d=res[row['key']];changed=d['status']=='validated_candidate';title='['+row['title']+'](badges/'+row['slug']+'/REPORT.md)' if changed or row['key']=='steel' else row['title'];state='Reviewed' if changed else ('Prior compact final retained' if row['key']=='astralNavigator' else ('Original retained after native review' if row['key']=='steel' else 'Already compact, retained'))
 text+=f"{title} | {d['before']['meshes']} | {d['after']['meshes']} | {d['before']['sections']} | {d['after']['sections']} | {state}\n"
text+='\nValidation and rebuild scripts are local to this folder. `compact.py` uses Blender’s bundled USD Python and the preserved baseline files. `blender_prepare.py` and `blender_review.py` use the live add on; `check_blender_files.py` finalizes only the standalone working copies. `install_preview.py` installs validated copies into the private preview. `capture.py` requires the intended badge to be visibly selected first, and checks the cached file hash as well as the actual scroll pose. The production application is never written by these scripts.\n'
assert '\u2014' not in text;(ROOT/'REPORT.md').write_text(text)
(ROOT/'completion.json').write_text(json.dumps(dict(status='complete',distinct_models=35,optimized_models=28,retained_already_compact=6,astral_retained=True,before=before,after=after,bytes_before=sizes[0],bytes_after=sizes[1],all_changed_models_reviewed=True,production_assets_preserved=True),indent=2)+'\n');print(json.dumps(dict(before=before,after=after,bytes=sizes,exports=len(exports)),indent=2))
