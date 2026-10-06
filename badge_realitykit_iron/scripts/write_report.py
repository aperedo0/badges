import json,hashlib,math,zipfile
from pathlib import Path
r=Path('/Users/antonioperedo/Downloads/badge_realitykit_iron')
original=json.loads((r/'reports/original_checksums.json').read_text());changed=[];missing=[]
for name,digest in original.items():
 p=Path(name)
 if not p.is_file():missing.append(name)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(name)
assert not changed and not missing,(changed,missing)
integrity={'original_files_checked':len(original),'changed':changed,'missing':missing,'reference_copy_identical':hashlib.sha256((r/'source/reference.png').read_bytes()).hexdigest()==hashlib.sha256(Path('/Users/antonioperedo/Downloads/Forged Iron Crystal Medallion.png').read_bytes()).hexdigest(),'app_repo_modified':False}
(r/'proof/original_integrity.json').write_text(json.dumps(integrity,indent=2))
geom=json.loads((r/'proof/geometry_identity.json').read_text());diff=json.loads((r/'proof/usd_diff_silver_vs_iron.json').read_text());tex=json.loads((r/'proof/texture_uniformity.json').read_text());model=json.loads((r/'reports/mobile_model.json').read_text())
# Store missing numerical measurements as null rather than non-standard JSON NaN.
def finite(v):
 if isinstance(v,float) and not math.isfinite(v):return None
 if isinstance(v,dict):return {k:finite(x) for k,x in v.items()}
 if isinstance(v,list):return [finite(x) for x in v]
 return v
for f in (r/'proof').glob('smoothness*.json'):
 data=json.loads(f.read_text());f.write_text(json.dumps(finite(data),indent=2,allow_nan=False))
materials=[
 ('Silver___circumferential_brushed_steel_Mobile_Casing','(0.150, 0.140, 0.125)',1,.325,'USDZ_Casing_base_color.png; USDZ_Casing_roughness.png'),
 ('Outer_edge___smooth_satin_silver_Mobile_Casing','(0.105, 0.102, 0.094)',1,.27,'USDZ_Casing_outer_base_color.png; USDZ_Casing_outer_roughness.png'),
 ('Back_and_edge___gunmetal_Mobile_Casing','(0.055, 0.052, 0.048)',.95,.32,'USDZ_Casing_back_base_color.png; USDZ_Casing_back_roughness.png'),
 ('Silver___polished_cut_edges_Mobile_Inner_edge','(0.300, 0.285, 0.260)',1,.19,'constant'),
 ('Silver___polished_cut_edges_Mobile_Rim_inner_lip','(0.300, 0.285, 0.260)',1,.19,'constant'),
 ('Emblem___satin_silver_facets_Mobile_Emblem','(0.360, 0.340, 0.300)',1,.29,'constant'),
 ('Emblem___shaded_outer_facets_Mobile_Emblem','(0.190, 0.180, 0.165)',1,.29,'constant'),
 ('Recess___smoked_nickel_Mobile_Inner_channel','(0.045, 0.043, 0.039)',1,.27,'constant'),
 ('Inset___finely_textured_charcoal_Mobile_Inset','(0.009, 0.010, 0.011)',.05,.83,'USDZ_Inset_base_color.png')]
lines=['# BestSpent Iron badge RealityKit handoff','',
 'Built in this new folder from a copy of the silver master. The emblem is an elongated irregular crystal with ten broad front planes, a slightly tilted ridge, asymmetric shoulders, and two iron facet tones. The reference supplied the silhouette and metal palette; its pitting, scratches, hammer marks and mottling were omitted.',
 '', '## Deliverables','',
 '- [RealityKit-ready USDZ](mobile/iron_badge_mobile.usdz) and [textures](mobile/textures/).',
 '- [Editable master](scenes/iron_medallion_master.blend), [reduced scene before rules](scenes/iron_badge_mobile_reduced.blend), and [final scene after rules](scenes/iron_badge_mobile.blend).',
 '- [Front with app point lights](proof/iron_front_app_lighting.png), [three-quarter at 45 degrees](proof/iron_three_quarter_app_lighting.png), [silver and iron at exactly the same scale](proof/silver_vs_iron_same_scale.png).',
 '- [Front facet crops](proof/all_facets_pose00.png), [20-degree facet crops](proof/all_facets_pose20.png), [45-degree facet crops](proof/all_facets_pose45.png); individual 4x crops under proof/facet_crops/. Rim, inset and whole-crystal 4x crops are in proof/.',
 '- [Smoothness numbers](proof/NUMBERS.md), the full JSON/TXT outputs, high-pass sheets, and render difference sheets under proof/.',
 '- [Additional real-time proof](proof/renders/iron_harsh_0_realtime.png) and [Cycles proof without denoising](proof/renders/iron_harsh_0_no_denoise.png).',
 '', '## Compatibility and geometry','',
 'The master casing, inner lip, inner edge, inner channel and inset mesh coordinates/topology retain the copied silver master exactly. Its nominal radius is 3.015, casing back Z approximately -0.345 and front Z approximately +0.260; this is the actual source profile, retained unchanged. The mobile enclosure copies the shipped v3 geometry exactly, including points, triangle indices, corner normals, extents, indexed UV arrays, geometry subsets and material assignments. Decimation was deliberately not rerun on these five meshes because the rules say it is not reproducible.',
 '', 'All six mesh prim names, all six object identifiers/display names, and all nine material IDs are unchanged. The crystal intentionally keeps the old spear IDs. No object, mesh or material name had to be dropped or renamed. Only the two unused inset normal shader helper prims were removed; they are neither objects nor materials. The brushed material prefix remains Silver___circumferential_brushed_steel so existing app anisotropy restoration continues to find it.',
 '', 'USD default prim /Badge, Y up, metersPerUnit 1, front +Z. All mesh world transforms are identity. Enclosure bounds match silver exactly. The new emblem bounds differ by at most 0.002595 units, less than 0.07% of its height; overall width/height/origin are unchanged. The maximum forward depth is 0.9748904 versus silver 0.9771203, a 0.0022299-unit reduction. This tiny intentional emblem change is fully listed in compare_usd output.',
 '', 'Every mesh is processed with the configured -2.895 floor. The frozen v3 casing already carries that cut, so the cut step is idempotent for it. Floor verification against the uncut handoff casing proves 26,245 kept triangles are bit-identical, 321 new cut triangles interpolate correctly, no kept triangles changed or disappeared, and no triangle lies below the floor. The nearest float32 value is -2.8949999809. There are 210 open boundary edges, all at the floor, zero non-manifold edges and no duplicate vertices; no cap.',
 '', '## Budget','',
 '| Asset | Silver v3 | Iron |', '|---|---:|---:|',
 f"| Triangles | {geom['total_triangles_silver']:,} | {geom['total_triangles_iron']:,} |",
 '| Emblem triangles | 230 | 98 |',
 f"| USDZ bytes | {geom['bytes_silver']:,} | {geom['bytes_iron']:,} |",
 f"| USDZ decimal MB | {geom['bytes_silver']/1e6:.3f} | {geom['bytes_iron']/1e6:.3f} |",
 '| Texture allocation | 3 x 512² plus 1 x 1024² | 7 x 512² |',
 '| Total texture pixels | 1,835,008 | 1,835,008 |',
 '', 'The enclosure triangle budgets are unchanged: casing 26,566, inset 3,570, inner channel 3,500, inner edge 2,200 and inner lip 2,500. Iron is 132 triangles smaller overall (0.34%) and its USDZ is 28.6% smaller because the uniform PNGs compress efficiently. No padding or hidden detail was added to approach 3.5 MB.',
 '', '## Materials','',
 'Colors below are nominal scene-linear RGB; constant color textures use sRGB PNG encoding and therefore have ordinary 8-bit quantization. Roughness textures are Non-Color. Each image has exactly one unique RGB triplet. Actual bytes and dimensions are recorded in proof/texture_uniformity.json. Metallic and roughness remain in the silver ranges. No normal map is exported, including on the flat inset.',
 '', '| Material ID (unchanged) | Linear RGB | Metallic | Roughness | Inputs |', '|---|---|---:|---:|---|']
for name,color,metal,rough,inputs in materials:lines.append(f'| `{name}` | {color} | {metal} | {rough} | {inputs} |')
lines += ['', 'The master brushed ring retains a UV tangent and anisotropy 0.48. USD cannot carry this anisotropy; as with silver, the app restores it using the preserved prefix. The proof imports show standard USD Preview Surface shading and do not exercise that app code.',
 '', '## Smoothness and inspection','',
 'Every broad crystal plane uses a constant corner normal. No noise nodes, bumps, normal maps, roughness variation or color variation can reach the mobile surface shaders. The new crystal bevel is 0.004 units with one segment and an explicit bevel material. The rule script folds all 64 bevel triangles into their owning facets, removes the temporary bevel material, keeps broad normals unchanged, and checks maximum strip width 0.007673 < 0.02. No widened glint was added. The inset bevel material is explicitly its existing inset slot; its geometry is unchanged.',
 '', 'Inspected the front, 20-degree and 45-degree facet sheets and rim/inset zooms. Broad facets and inset look smooth; the ring has continuous physical light reflections and its original profile. Point lights produce angular cast-shadow silhouettes on the inset and strong neighboring facet contrast. Those shadows and true highlight gradients are retained in the proof rather than retouched. At 4x nearest-neighbor enlargement, raster stair steps and 8-bit quantization can be seen at edges; these are not baked texture seams.',
 '', 'The usual supplied Cycles proof uses denoising, so an extra 512-sample proof without denoising was also made. It exhibits Monte Carlo glossy/indirect noise on a few dark facets (mean facet grain 2.01, largest facet residual 6.91). That output and its numbers are retained openly. A separate Eevee real-time point-light proof without ray-traced indirect bounces and without denoising gives mean facet grain 0.19 and mean residual 0.22. The identical uniform textures and constant facet normals were validated independently. The Eevee proof omits ray-traced floor reflection; it is a surface diagnostic, not a replacement for the standard stage proofs or an iPhone test.',
 '', 'The ring high-pass metric includes its curved highlight profile; it is not a pure texture-noise measurement. Edge excess includes real contrast between adjacent facets, and does not by itself imply a bevel glint. At 45 degrees the standard ring mask has too few eroded pixels for its mottle value; that unavailable measurement is null in JSON and nan in the script TXT output. No substitute number was invented.',
 '', '## Pipeline and checks','',
 'Read the supplied EXPORT_RULES.md, HANDOFF.md and all nine requested scripts first. All copied script edits are confined here. build_iron.py opens only source/silver_master.blend, replaces only the emblem mesh, updates material nodes, and writes the master. The copied export_mobile.py reconstructs the new emblem from evaluated master geometry and uses frozen v3 enclosure arrays. Its output names/default paths are adapted to this folder, and the inset normal connection is omitted. badge_mobile_rules.py applies rules 1–6 with the unchanged silver config and -2.895 floor; a final CopySpec restores the five exact shipped enclosure specifications, including indexed UV representation.',
 '', 'The full export ran from iron_medallion_master.blend, saved the reduced scene, then applied badge_mobile_rules.py and saved the final scene/USDZ. Subsequent checks confirm the reduced/final Blender positions and triangles match the USDZ, broad normals are constant, and all metal/inset normal connections are absent.',
 '', 'Checks completed: usdchecker --arkit (Success, with the same known duplicate GeomSubset registration diagnostics documented by the silver handoff); reimport_check.py (six meshes, nine materials, custom normals, packed textures); verify_floor_cut.py; compare_usd.py; check_casing_topology.py; render_proof.py for master/silver/iron under stage and app point rigs at 0 and 20 degrees, plus iron 45 degrees; measure_smoothness.py; make_proof_sheets.py; compare_renders.py; texture uniformity; editable scene validation; original-file integrity.',
 '', 'One concurrently run 45-degree Blender render saved a valid image but aborted during process cleanup with a mutex exception. It was rerun in isolation and exited cleanly; the successful rerun replaced the delivered image. The diagnostic log remains logs/render_iron_harsh_45.log and the successful log is logs/render_iron_harsh_45_retry.log.',
 '', '## All USD differences','',
 f"compare_usd.py reports {len(diff['differences'])} authored changes. None are on an enclosure mesh/object. There are nine changes on the replaced emblem (extent, topology, normals, points, UV layout and two material subset index arrays), four casing texture asset-path changes for the outer/back slots, five material color changes, and three removed inset-normal graph items. Texture pixel content changes do not appear in compare_usd; the seven uniform texture inputs are documented below. This is the complete machine-readable difference list:",
 '', '```json',json.dumps(diff['differences'],indent=2),'```',
 '', '## Integrity and remaining uncertainty','',
 f"All {len(original)} files present in the original v3 and handoff folders were hashed before work and rechecked after work: zero changed or missing files. The reference image was copied exactly. The app repository was not modified. The geometry and file checks are complete; actual RealityKit rendering on a phone and the app's restored anisotropy remain untested because app integration is separate. The Blender app rig uses the positions/colors and lumen-to-watt conversion in the supplied proof script; it cannot guarantee exact renderer/color-management equivalence to RealityKit.",
 '', '## Complete check outputs','']
for path in ['logs/build.log','logs/export.log','proof/geometry_identity.txt','proof/scene_and_normals_validation.txt','proof/usdchecker.log','proof/reimport_check.txt','proof/floor_cut_verification.txt','proof/floor_cut_topology.txt','proof/usd_diff_silver_vs_iron.txt','proof/proof_analysis.txt','proof/smoothness_pose00.txt','proof/smoothness_pose20.txt','proof/smoothness_pose45.txt','proof/smoothness_silver_pose00.txt','proof/smoothness_silver_pose20.txt','proof/smoothness_no_denoise.txt','proof/smoothness_realtime.txt']:
 lines += [f'### {path}','', '```text',(r/path).read_text(),'```','']
for path in ['proof/texture_uniformity.json','proof/scene_and_normals_validation.json','proof/original_integrity.json']:
 lines += [f'### {path}','', '```json',(r/path).read_text(),'```','']
lines += ['### render_proof.py outputs','', 'All successful render logs are provided under logs/render_*.log. Each lists the six imported meshes and its RENDERED output path. All proof PNGs have been decoded successfully. Full per-facet and per-region numeric arrays are in proof/smoothness_*.json and proof/render_diff_silver_vs_iron.json. High-pass images were made only in separate proof sheets; original renders and the asset were not retouched.','']
(r/'REPORT.md').write_text('\n'.join(lines))
num=['# Smoothness measurements','','Display Rec.709 luma levels on the 0–255 8-bit proof image. Broad facet masks exclude the pre-rule polished bevel assignments.','','| Render | Mean facet residual | Mean facet grain | Ring grain | Ring mottle | Inset L grain | Inset R grain |','|---|---:|---:|---:|---:|---:|---:|']
for name in ['smoothness_pose00','smoothness_pose20','smoothness_pose45','smoothness_silver_pose00','smoothness_silver_pose20','smoothness_no_denoise','smoothness_realtime']:
 d=json.loads((r/f'proof/{name}.json').read_text())
 for key,v in d['table'].items():
  values=[v['facet_rough_mean'],v['facet_grain_mean'],v['ring']['grain'],v['ring']['mottle'],v['inset-left']['grain'],v['inset-right']['grain']]
  num.append('| '+f"{key}, pose {d['pose']:g}"+' | '+' | '.join('N/A' if x is None else f'{x:.3f}' for x in values)+' |')
num += ['', 'N/A: too few pixels survive the supplied mask erosion at 45 degrees. Ring metrics include physical curvature/highlight variation. The raw Cycles proof retains Monte Carlo indirect noise; the real-time proof uses Eevee with denoising and ray-traced indirect bounces disabled. Full per-facet, edge and patch values are in the corresponding JSON/TXT files. See REPORT.md for interpretation and limitations.']
(r/'proof/NUMBERS.md').write_text('\n'.join(num))
# Manifest omits the disposable Python dependency environment and pycache.
files=sorted(p for p in r.rglob('*') if p.is_file() and 'analysis_env' not in p.parts and '__pycache__' not in p.parts and p.name!='FILE_MANIFEST.txt')
(r/'FILE_MANIFEST.txt').write_text('\n'.join(str(p.relative_to(r)) for p in files)+'\n')
print('REPORT written; originals verified; delivery files',len(files))
