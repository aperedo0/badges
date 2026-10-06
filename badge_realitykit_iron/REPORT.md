# BestSpent Iron badge RealityKit handoff

Built in this new folder from a copy of the silver master. The emblem is an elongated irregular crystal with ten broad front planes, a slightly tilted ridge, asymmetric shoulders, and two iron facet tones. The reference supplied the silhouette and metal palette; its pitting, scratches, hammer marks and mottling were omitted.

## Deliverables

- [RealityKit-ready USDZ](mobile/iron_badge_mobile.usdz) and [textures](mobile/textures/).
- [Editable master](scenes/iron_medallion_master.blend), [reduced scene before rules](scenes/iron_badge_mobile_reduced.blend), and [final scene after rules](scenes/iron_badge_mobile.blend).
- [Front with app point lights](proof/iron_front_app_lighting.png), [three-quarter at 45 degrees](proof/iron_three_quarter_app_lighting.png), [silver and iron at exactly the same scale](proof/silver_vs_iron_same_scale.png).
- [Front facet crops](proof/all_facets_pose00.png), [20-degree facet crops](proof/all_facets_pose20.png), [45-degree facet crops](proof/all_facets_pose45.png); individual 4x crops under proof/facet_crops/. Rim, inset and whole-crystal 4x crops are in proof/.
- [Smoothness numbers](proof/NUMBERS.md), the full JSON/TXT outputs, high-pass sheets, and render difference sheets under proof/.
- [Additional real-time proof](proof/renders/iron_harsh_0_realtime.png) and [Cycles proof without denoising](proof/renders/iron_harsh_0_no_denoise.png).

## Compatibility and geometry

The master casing, inner lip, inner edge, inner channel and inset mesh coordinates/topology retain the copied silver master exactly. Its nominal radius is 3.015, casing back Z approximately -0.345 and front Z approximately +0.260; this is the actual source profile, retained unchanged. The mobile enclosure copies the shipped v3 geometry exactly, including points, triangle indices, corner normals, extents, indexed UV arrays, geometry subsets and material assignments. Decimation was deliberately not rerun on these five meshes because the rules say it is not reproducible.

All six mesh prim names, all six object identifiers/display names, and all nine material IDs are unchanged. The crystal intentionally keeps the old spear IDs. No object, mesh or material name had to be dropped or renamed. Only the two unused inset normal shader helper prims were removed; they are neither objects nor materials. The brushed material prefix remains Silver___circumferential_brushed_steel so existing app anisotropy restoration continues to find it.

USD default prim /Badge, Y up, metersPerUnit 1, front +Z. All mesh world transforms are identity. Enclosure bounds match silver exactly. The new emblem bounds differ by at most 0.002595 units, less than 0.07% of its height; overall width/height/origin are unchanged. The maximum forward depth is 0.9748904 versus silver 0.9771203, a 0.0022299-unit reduction. This tiny intentional emblem change is fully listed in compare_usd output.

Every mesh is processed with the configured -2.895 floor. The frozen v3 casing already carries that cut, so the cut step is idempotent for it. Floor verification against the uncut handoff casing proves 26,245 kept triangles are bit-identical, 321 new cut triangles interpolate correctly, no kept triangles changed or disappeared, and no triangle lies below the floor. The nearest float32 value is -2.8949999809. There are 210 open boundary edges, all at the floor, zero non-manifold edges and no duplicate vertices; no cap.

## Budget

| Asset | Silver v3 | Iron |
|---|---:|---:|
| Triangles | 38,566 | 38,434 |
| Emblem triangles | 230 | 98 |
| USDZ bytes | 3,511,448 | 2,506,612 |
| USDZ decimal MB | 3.511 | 2.507 |
| Texture allocation | 3 x 512² plus 1 x 1024² | 7 x 512² |
| Total texture pixels | 1,835,008 | 1,835,008 |

The enclosure triangle budgets are unchanged: casing 26,566, inset 3,570, inner channel 3,500, inner edge 2,200 and inner lip 2,500. Iron is 132 triangles smaller overall (0.34%) and its USDZ is 28.6% smaller because the uniform PNGs compress efficiently. No padding or hidden detail was added to approach 3.5 MB.

## Materials

Colors below are nominal scene-linear RGB; constant color textures use sRGB PNG encoding and therefore have ordinary 8-bit quantization. Roughness textures are Non-Color. Each image has exactly one unique RGB triplet. Actual bytes and dimensions are recorded in proof/texture_uniformity.json. Metallic and roughness remain in the silver ranges. No normal map is exported, including on the flat inset.

| Material ID (unchanged) | Linear RGB | Metallic | Roughness | Inputs |
|---|---|---:|---:|---|
| `Silver___circumferential_brushed_steel_Mobile_Casing` | (0.150, 0.140, 0.125) | 1 | 0.325 | USDZ_Casing_base_color.png; USDZ_Casing_roughness.png |
| `Outer_edge___smooth_satin_silver_Mobile_Casing` | (0.105, 0.102, 0.094) | 1 | 0.27 | USDZ_Casing_outer_base_color.png; USDZ_Casing_outer_roughness.png |
| `Back_and_edge___gunmetal_Mobile_Casing` | (0.055, 0.052, 0.048) | 0.95 | 0.32 | USDZ_Casing_back_base_color.png; USDZ_Casing_back_roughness.png |
| `Silver___polished_cut_edges_Mobile_Inner_edge` | (0.300, 0.285, 0.260) | 1 | 0.19 | constant |
| `Silver___polished_cut_edges_Mobile_Rim_inner_lip` | (0.300, 0.285, 0.260) | 1 | 0.19 | constant |
| `Emblem___satin_silver_facets_Mobile_Emblem` | (0.360, 0.340, 0.300) | 1 | 0.29 | constant |
| `Emblem___shaded_outer_facets_Mobile_Emblem` | (0.190, 0.180, 0.165) | 1 | 0.29 | constant |
| `Recess___smoked_nickel_Mobile_Inner_channel` | (0.045, 0.043, 0.039) | 1 | 0.27 | constant |
| `Inset___finely_textured_charcoal_Mobile_Inset` | (0.009, 0.010, 0.011) | 0.05 | 0.83 | USDZ_Inset_base_color.png |

The master brushed ring retains a UV tangent and anisotropy 0.48. USD cannot carry this anisotropy; as with silver, the app restores it using the preserved prefix. The proof imports show standard USD Preview Surface shading and do not exercise that app code.

## Smoothness and inspection

Every broad crystal plane uses a constant corner normal. No noise nodes, bumps, normal maps, roughness variation or color variation can reach the mobile surface shaders. The new crystal bevel is 0.004 units with one segment and an explicit bevel material. The rule script folds all 64 bevel triangles into their owning facets, removes the temporary bevel material, keeps broad normals unchanged, and checks maximum strip width 0.007673 < 0.02. No widened glint was added. The inset bevel material is explicitly its existing inset slot; its geometry is unchanged.

Inspected the front, 20-degree and 45-degree facet sheets and rim/inset zooms. Broad facets and inset look smooth; the ring has continuous physical light reflections and its original profile. Point lights produce angular cast-shadow silhouettes on the inset and strong neighboring facet contrast. Those shadows and true highlight gradients are retained in the proof rather than retouched. At 4x nearest-neighbor enlargement, raster stair steps and 8-bit quantization can be seen at edges; these are not baked texture seams.

The usual supplied Cycles proof uses denoising, so an extra 512-sample proof without denoising was also made. It exhibits Monte Carlo glossy/indirect noise on a few dark facets (mean facet grain 2.01, largest facet residual 6.91). That output and its numbers are retained openly. A separate Eevee real-time point-light proof without ray-traced indirect bounces and without denoising gives mean facet grain 0.19 and mean residual 0.22. The identical uniform textures and constant facet normals were validated independently. The Eevee proof omits ray-traced floor reflection; it is a surface diagnostic, not a replacement for the standard stage proofs or an iPhone test.

The ring high-pass metric includes its curved highlight profile; it is not a pure texture-noise measurement. Edge excess includes real contrast between adjacent facets, and does not by itself imply a bevel glint. At 45 degrees the standard ring mask has too few eroded pixels for its mottle value; that unavailable measurement is null in JSON and nan in the script TXT output. No substitute number was invented.

## Pipeline and checks

Read the supplied EXPORT_RULES.md, HANDOFF.md and all nine requested scripts first. All copied script edits are confined here. build_iron.py opens only source/silver_master.blend, replaces only the emblem mesh, updates material nodes, and writes the master. The copied export_mobile.py reconstructs the new emblem from evaluated master geometry and uses frozen v3 enclosure arrays. Its output names/default paths are adapted to this folder, and the inset normal connection is omitted. badge_mobile_rules.py applies rules 1–6 with the unchanged silver config and -2.895 floor; a final CopySpec restores the five exact shipped enclosure specifications, including indexed UV representation.

The full export ran from iron_medallion_master.blend, saved the reduced scene, then applied badge_mobile_rules.py and saved the final scene/USDZ. Subsequent checks confirm the reduced/final Blender positions and triangles match the USDZ, broad normals are constant, and all metal/inset normal connections are absent.

Checks completed: usdchecker --arkit (Success, with the same known duplicate GeomSubset registration diagnostics documented by the silver handoff); reimport_check.py (six meshes, nine materials, custom normals, packed textures); verify_floor_cut.py; compare_usd.py; check_casing_topology.py; render_proof.py for master/silver/iron under stage and app point rigs at 0 and 20 degrees, plus iron 45 degrees; measure_smoothness.py; make_proof_sheets.py; compare_renders.py; texture uniformity; editable scene validation; original-file integrity.

One concurrently run 45-degree Blender render saved a valid image but aborted during process cleanup with a mutex exception. It was rerun in isolation and exited cleanly; the successful rerun replaced the delivered image. The diagnostic log remains logs/render_iron_harsh_45.log and the successful log is logs/render_iron_harsh_45_retry.log.

## All USD differences

compare_usd.py reports 21 authored changes. None are on an enclosure mesh/object. There are nine changes on the replaced emblem (extent, topology, normals, points, UV layout and two material subset index arrays), four casing texture asset-path changes for the outer/back slots, five material color changes, and three removed inset-normal graph items. Texture pixel content changes do not appear in compare_usd; the seven uniform texture inputs are documented below. This is the complete machine-readable difference list:

```json
[
  {
    "prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry",
    "attr": "extent",
    "change": "values",
    "max_abs_delta": 0.0025949478149414062,
    "elements_changed": 2,
    "elements": 2
  },
  {
    "prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry",
    "attr": "faceVertexCounts",
    "change": "array shape",
    "old": [
      230
    ],
    "new": [
      98
    ]
  },
  {
    "prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry",
    "attr": "faceVertexIndices",
    "change": "array shape",
    "old": [
      690
    ],
    "new": [
      294
    ]
  },
  {
    "prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry",
    "attr": "normals",
    "change": "array shape",
    "old": [
      690,
      3
    ],
    "new": [
      294,
      3
    ]
  },
  {
    "prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry",
    "attr": "points",
    "change": "array shape",
    "old": [
      117,
      3
    ],
    "new": [
      51,
      3
    ]
  },
  {
    "prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry",
    "attr": "primvars:USDZ_UV",
    "change": "array shape",
    "old": [
      170,
      2
    ],
    "new": [
      51,
      2
    ]
  },
  {
    "prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry",
    "attr": "primvars:USDZ_UV:indices",
    "change": "array shape",
    "old": [
      690
    ],
    "new": [
      294
    ]
  },
  {
    "prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry/Emblem___satin_silver_facets_Mobile_Emblem",
    "attr": "indices",
    "change": "array shape",
    "old": [
      180
    ],
    "new": [
      34
    ]
  },
  {
    "prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry/Emblem___shaded_outer_facets_Mobile_Emblem",
    "attr": "indices",
    "change": "array shape",
    "old": [
      50
    ],
    "new": [
      64
    ]
  },
  {
    "prim": "/Badge/_materials/Back_and_edge___gunmetal_Mobile_Casing/Image_Texture",
    "attr": "inputs:file",
    "change": "value",
    "old": "@./textures/USDZ_Casing_base_color.png@",
    "new": "@./textures/USDZ_Casing_back_base_color.png@"
  },
  {
    "prim": "/Badge/_materials/Back_and_edge___gunmetal_Mobile_Casing/Image_Texture_001",
    "attr": "inputs:file",
    "change": "value",
    "old": "@./textures/USDZ_Casing_roughness.png@",
    "new": "@./textures/USDZ_Casing_back_roughness.png@"
  },
  {
    "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Principled_BSDF",
    "attr": "inputs:diffuseColor",
    "change": "values",
    "max_abs_delta": 0.20000001788139343,
    "elements_changed": 3,
    "elements": 3
  },
  {
    "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Principled_BSDF",
    "attr": "inputs:diffuseColor",
    "change": "values",
    "max_abs_delta": 0.019999995827674866,
    "elements_changed": 3,
    "elements": 3
  },
  {
    "prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Image_Texture_001",
    "change": "removed",
    "type": "Shader"
  },
  {
    "prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Principled_BSDF",
    "attr": "inputs:normal",
    "change": "attribute removed"
  },
  {
    "prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/UV_Map_001",
    "change": "removed",
    "type": "Shader"
  },
  {
    "prim": "/Badge/_materials/Outer_edge___smooth_satin_silver_Mobile_Casing/Image_Texture",
    "attr": "inputs:file",
    "change": "value",
    "old": "@./textures/USDZ_Casing_base_color.png@",
    "new": "@./textures/USDZ_Casing_outer_base_color.png@"
  },
  {
    "prim": "/Badge/_materials/Outer_edge___smooth_satin_silver_Mobile_Casing/Image_Texture_001",
    "attr": "inputs:file",
    "change": "value",
    "old": "@./textures/USDZ_Casing_roughness.png@",
    "new": "@./textures/USDZ_Casing_outer_roughness.png@"
  },
  {
    "prim": "/Badge/_materials/Recess___smoked_nickel_Mobile_Inner_channel/Principled_BSDF",
    "attr": "inputs:diffuseColor",
    "change": "values",
    "max_abs_delta": 0.02499999850988388,
    "elements_changed": 3,
    "elements": 3
  },
  {
    "prim": "/Badge/_materials/Silver___polished_cut_edges_Mobile_Inner_edge/Principled_BSDF",
    "attr": "inputs:diffuseColor",
    "change": "values",
    "max_abs_delta": 0.3399999737739563,
    "elements_changed": 3,
    "elements": 3
  },
  {
    "prim": "/Badge/_materials/Silver___polished_cut_edges_Mobile_Rim_inner_lip/Principled_BSDF",
    "attr": "inputs:diffuseColor",
    "change": "values",
    "max_abs_delta": 0.3399999737739563,
    "elements_changed": 3,
    "elements": 3
  }
]
```

## Integrity and remaining uncertainty

All 105 files present in the original v3 and handoff folders were hashed before work and rechecked after work: zero changed or missing files. The reference image was copied exactly. The app repository was not modified. The geometry and file checks are complete; actual RealityKit rendering on a phone and the app's restored anisotropy remain untested because app integration is separate. The Blender app rig uses the positions/colors and lumen-to-watt conversion in the supplied proof script; it cannot guarantee exact renderer/color-management equivalence to RealityKit.

## Complete check outputs

### logs/build.log

```text
00:01.924  blend            | Read blend: "/Users/antonioperedo/Downloads/badge_realitykit_iron/source/silver_master.blend"
Info: Saved as "iron_medallion_master.blend"
NEW CRYSTAL 98 triangles [-1.0869447  -2.0447795   0.11999981] [1.0870531 2.0148818 0.9748904]
IRON MASTER BUILT; ENCLOSURE UNTOUCHED
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)

Blender quit

```

### logs/export.log

```text
00:01.222  blend            | Read blend: "/Users/antonioperedo/Downloads/badge_realitykit_iron/scenes/iron_medallion_master.blend"
/Users/antonioperedo/Downloads/badge_realitykit_iron/scripts/export_mobile.py:76: DeprecationWarning: 'Material.use_nodes' is expected to be removed in Blender 6.0
  mat=bpy.data.materials.new(src.name+' Mobile '+short);mat.use_nodes=True
Info: Saved as "iron_badge_mobile_reduced.blend"
Info: Saved as "iron_badge_mobile.blend"
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)
USD export of '/Users/antonioperedo/Downloads/badge_realitykit_iron/mobile/iron_badge_mobile.usdc' took 39.48 ms

Blender quit

```

### proof/geometry_identity.txt

```text
00:01.686  blend            | Read blend: "/Users/antonioperedo/Downloads/badge_realitykit_iron/scenes/iron_medallion_master.blend"
PASS: all five enclosure meshes exact; all six mesh and nine material names exact; Y-up/meters/identity transforms/floor correct; master enclosure unchanged
{
  "total_triangles_silver": 38566,
  "total_triangles_iron": 38434,
  "bytes_silver": 3511448,
  "bytes_iron": 2506612
}
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)

Blender quit

```

### proof/scene_and_normals_validation.txt

```text
00:00.991  blend            | Read blend: "/Users/antonioperedo/Downloads/badge_realitykit_iron/scenes/iron_badge_mobile_reduced.blend"
00:01.152  blend            | Read blend: "/Users/antonioperedo/Downloads/badge_realitykit_iron/scenes/iron_badge_mobile.blend"
PASS: reduced/final scene mesh positions and triangles match USDZ; broad facet corner normals are constant; no exported normal maps.
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)

Blender quit

```

### proof/usdchecker.log

```text
Coding Error: in RegisterBehaviorForPrimTypeId at line 454 of usdShade/connectableAPIBehavior.cpp -- UsdShade Connectable behavior already registered for primTypeId comprised of 'GeomSubset;MaterialBindingAPI' type and apischemas.
Coding Error: in RegisterBehaviorForPrimTypeId at line 454 of usdShade/connectableAPIBehavior.cpp -- UsdShade Connectable behavior already registered for primTypeId comprised of 'GeomSubset;MaterialBindingAPI' type and apischemas.
Coding Error: in RegisterBehaviorForPrimTypeId at line 454 of usdShade/connectableAPIBehavior.cpp -- UsdShade Connectable behavior already registered for primTypeId comprised of 'GeomSubset;MaterialBindingAPI' type and apischemas.

Validation Result with no explicit variants set
Success!

```

### proof/reimport_check.txt

```text
Info: Fixed mesh for prim: /Badge/Casing___smooth_rounded_outer_edge/Casing___smooth_rounded_outer_edge_mobile_geometry
Info: Fixed mesh for prim: /Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry
Info: Fixed mesh for prim: /Badge/Inner_channel___shadowed_bevel/Inner_channel___shadowed_bevel_mobile_geometry
Info: Fixed mesh for prim: /Badge/Inner_edge___fine_silver_reveal/Inner_edge___fine_silver_reveal_mobile_geometry
Info: Fixed mesh for prim: /Badge/Inset___charcoal_textured_disk/Inset___charcoal_textured_disk_mobile_geometry
Info: Fixed mesh for prim: /Badge/Rim_inner_lip___narrow_highlight/Rim_inner_lip___narrow_highlight_mobile_geometry
import result {'FINISHED'}
MESH Casing___smooth_rounded_outer_edge_mobile_geometry: 13389 verts, 26566 tris, custom normals True, UVs ['Machining_UV', 'USDZ_UV'], local bounds min [-3.01487, -2.895, -0.345] max [3.01487, 3.01487, 0.26002]
    material Outer_edge___smooth_satin_silver_Mobile_Casing: 20384 faces
    material Silver___circumferential_brushed_steel_Mobile_Casing: 4950 faces
    material Back_and_edge___gunmetal_Mobile_Casing: 1232 faces
MESH Emblem___faceted_compass_spear_mobile_geometry: 51 verts, 98 tris, custom normals True, UVs ['USDZ_UV'], local bounds min [-1.08694, -2.04478, 0.12] max [1.08705, 2.01488, 0.97489]
    material Emblem___satin_silver_facets_Mobile_Emblem: 34 faces
    material Emblem___shaded_outer_facets_Mobile_Emblem: 64 faces
MESH Inner_channel___shadowed_bevel_mobile_geometry: 1750 verts, 3500 tris, custom normals True, UVs ['Machining_UV'], local bounds min [-2.6401, -2.6401, 0.01799] max [2.6401, 2.6401, 0.20115]
    material Recess___smoked_nickel_Mobile_Inner_channel: 3500 faces
MESH Inner_edge___fine_silver_reveal_mobile_geometry: 1100 verts, 2200 tris, custom normals True, UVs ['Machining_UV'], local bounds min [-2.53907, -2.53907, 0.06099] max [2.53907, 2.53907, 0.09602]
    material Silver___polished_cut_edges_Mobile_Inner_edge: 2200 faces
MESH Inset___charcoal_textured_disk_mobile_geometry: 1787 verts, 3570 tris, custom normals True, UVs ['USDZ_UV', 'UVMap'], local bounds min [-2.525, -2.525, -0.131] max [2.525, 2.525, 0.039]
    material Inset___finely_textured_charcoal_Mobile_Inset: 3570 faces
MESH Rim_inner_lip___narrow_highlight_mobile_geometry: 1250 verts, 2500 tris, custom normals True, UVs ['Machining_UV'], local bounds min [-2.66122, -2.66122, 0.18692] max [2.66122, 2.66122, 0.22402]
    material Silver___polished_cut_edges_Mobile_Rim_inner_lip: 2500 faces
OBJECT _materials (EMPTY)
TOTAL TRIANGLES 38434
MATERIAL Back_and_edge___gunmetal_Mobile_Casing: base color texture, {'Metallic': 0.95}, linked inputs {'Base Color': 'TEX_IMAGE', 'Roughness': 'SEPARATE_COLOR'}, images ['USDZ_Casing_back_base_color.png', 'USDZ_Casing_back_roughness.png']
MATERIAL Emblem___satin_silver_facets_Mobile_Emblem: base color (0.36, 0.34, 0.3), {'Metallic': 1.0, 'Roughness': 0.29}, linked inputs {}, images []
MATERIAL Emblem___shaded_outer_facets_Mobile_Emblem: base color (0.19, 0.18, 0.165), {'Metallic': 1.0, 'Roughness': 0.29}, linked inputs {}, images []
MATERIAL Inset___finely_textured_charcoal_Mobile_Inset: base color texture, {'Metallic': 0.05, 'Roughness': 0.83}, linked inputs {'Base Color': 'TEX_IMAGE'}, images ['USDZ_Inset_base_color.png']
MATERIAL Outer_edge___smooth_satin_silver_Mobile_Casing: base color texture, {'Metallic': 1.0}, linked inputs {'Base Color': 'TEX_IMAGE', 'Roughness': 'SEPARATE_COLOR'}, images ['USDZ_Casing_outer_base_color.png', 'USDZ_Casing_outer_roughness.png']
MATERIAL Recess___smoked_nickel_Mobile_Inner_channel: base color (0.045, 0.043, 0.039), {'Metallic': 1.0, 'Roughness': 0.27}, linked inputs {}, images []
MATERIAL Silver___circumferential_brushed_steel_Mobile_Casing: base color texture, {'Metallic': 1.0}, linked inputs {'Base Color': 'TEX_IMAGE', 'Roughness': 'SEPARATE_COLOR'}, images ['USDZ_Casing_base_color.png', 'USDZ_Casing_roughness.png']
MATERIAL Silver___polished_cut_edges_Mobile_Inner_edge: base color (0.3, 0.285, 0.26), {'Metallic': 1.0, 'Roughness': 0.19}, linked inputs {}, images []
MATERIAL Silver___polished_cut_edges_Mobile_Rim_inner_lip: base color (0.3, 0.285, 0.26), {'Metallic': 1.0, 'Roughness': 0.19}, linked inputs {}, images []
IMAGE USDZ_Casing_back_base_color.png: 512x512, sRGB, packed True
IMAGE USDZ_Casing_back_roughness.png: 512x512, Non-Color, packed True
IMAGE USDZ_Casing_base_color.png: 512x512, sRGB, packed True
IMAGE USDZ_Casing_outer_base_color.png: 512x512, sRGB, packed True
IMAGE USDZ_Casing_outer_roughness.png: 512x512, Non-Color, packed True
IMAGE USDZ_Casing_roughness.png: 512x512, Non-Color, packed True
IMAGE USDZ_Inset_base_color.png: 512x512, sRGB, packed True
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)
USD import of '/Users/antonioperedo/Downloads/badge_realitykit_iron/mobile/iron_badge_mobile.usdz' took 104.43 ms

Blender quit

```

### proof/floor_cut_verification.txt

```text
{
 "uncut": "/Users/antonioperedo/Downloads/badge_realitykit_iron/work/iron_uncut.usdz",
 "cut": "/Users/antonioperedo/Downloads/badge_realitykit_iron/mobile/iron_badge_mobile.usdz",
 "height": -2.895,
 "meshes": {
  "Inset___charcoal_textured_disk_mobile_geometry": {
   "min_y_uncut": -2.5250000953674316,
   "min_y_cut": -2.5250000953674316,
   "max_uncut": [
    2.5250000953674316,
    2.5250000953674316,
    0.03900047391653061
   ],
   "max_cut": [
    2.5250000953674316,
    2.5250000953674316,
    0.03900047391653061
   ],
   "triangles_uncut": 3570,
   "triangles_cut": 3570,
   "byte_identical": true,
   "sha1_uncut": "2c272b78487abb62e061ff6c6adaf8e4014e6615",
   "sha1_cut": "2c272b78487abb62e061ff6c6adaf8e4014e6615"
  },
  "Inner_edge___fine_silver_reveal_mobile_geometry": {
   "min_y_uncut": -2.5390655994415283,
   "min_y_cut": -2.5390655994415283,
   "max_uncut": [
    2.5390655994415283,
    2.5390655994415283,
    0.09602090716362
   ],
   "max_cut": [
    2.5390655994415283,
    2.5390655994415283,
    0.09602090716362
   ],
   "triangles_uncut": 2200,
   "triangles_cut": 2200,
   "byte_identical": true,
   "sha1_uncut": "dce1bf67dc3cb55576456a2c0cde22d829982c83",
   "sha1_cut": "dce1bf67dc3cb55576456a2c0cde22d829982c83"
  },
  "Casing___smooth_rounded_outer_edge_mobile_geometry": {
   "min_y_uncut": -3.01487135887146,
   "min_y_cut": -2.8949999809265137,
   "max_uncut": [
    3.01487135887146,
    3.01487135887146,
    0.2600186765193939
   ],
   "max_cut": [
    3.01487135887146,
    3.01487135887146,
    0.2600186765193939
   ],
   "triangles_uncut": 28000,
   "triangles_cut": 26566,
   "byte_identical": false,
   "sha1_uncut": "525449b90b7bfd4772379907fb78ed80fdb92298",
   "sha1_cut": "5efcee30005e669fda6759793ccfcc2b791bcc93",
   "uncut_triangles_above": 26245,
   "uncut_triangles_below": 1545,
   "uncut_triangles_crossing": 210,
   "kept_bit_identical": 26245,
   "kept_changed": 0,
   "kept_missing": 0,
   "new_cut_triangles": 321,
   "new_triangle_material_mismatches": 0,
   "new_corner_normal_max_deg_from_edge_interpolation": 8.79013768592829e-06,
   "new_corner_uv_max_abs_from_edge_interpolation": 7.326423778764024e-08,
   "new_triangle_max_distance_from_source_plane": 8.44377321182268e-09,
   "max_depth_below_floor": 0.0
  },
  "Emblem___faceted_compass_spear_mobile_geometry": {
   "min_y_uncut": -2.0447795391082764,
   "min_y_cut": -2.0447795391082764,
   "max_uncut": [
    1.0870530605316162,
    2.0148818492889404,
    0.974890410900116
   ],
   "max_cut": [
    1.0870530605316162,
    2.0148818492889404,
    0.974890410900116
   ],
   "triangles_uncut": 98,
   "triangles_cut": 98,
   "byte_identical": true,
   "sha1_uncut": "c4f99d9f292c7b622e704eabe989cd6a4f8f046a",
   "sha1_cut": "c4f99d9f292c7b622e704eabe989cd6a4f8f046a"
  },
  "Inner_channel___shadowed_bevel_mobile_geometry": {
   "min_y_uncut": -2.6401007175445557,
   "min_y_cut": -2.6401007175445557,
   "max_uncut": [
    2.6401007175445557,
    2.6401007175445557,
    0.20115379989147186
   ],
   "max_cut": [
    2.6401007175445557,
    2.6401007175445557,
    0.20115379989147186
   ],
   "triangles_uncut": 3500,
   "triangles_cut": 3500,
   "byte_identical": true,
   "sha1_uncut": "f607effc8b3fcc079436407e2084260fce7e1e15",
   "sha1_cut": "f607effc8b3fcc079436407e2084260fce7e1e15"
  },
  "Rim_inner_lip___narrow_highlight_mobile_geometry": {
   "min_y_uncut": -2.6612191200256348,
   "min_y_cut": -2.6612191200256348,
   "max_uncut": [
    2.6612191200256348,
    2.6612191200256348,
    0.22401870787143707
   ],
   "max_cut": [
    2.6612191200256348,
    2.6612191200256348,
    0.22401870787143707
   ],
   "triangles_uncut": 2500,
   "triangles_cut": 2500,
   "byte_identical": true,
   "sha1_uncut": "084285305a05657fda0fbff09aa9729d51d04950",
   "sha1_cut": "084285305a05657fda0fbff09aa9729d51d04950"
  }
 }
}
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)

Blender quit

```

### proof/floor_cut_topology.txt

```text
source edges 39954 boundary 210 on floor 210 non-manifold 0 points 13389 unique positions 13389
badge_realitykit_iron edges 39954 boundary 210 on floor 210 non-manifold 0 points 13389 unique positions 13389
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)

Blender quit

```

### proof/usd_diff_silver_vs_iron.txt

```text
stage {"old": {"upAxis": "Y", "metersPerUnit": 1.0, "defaultPrim": "/Badge"}, "new": {"upAxis": "Y", "metersPerUnit": 1.0, "defaultPrim": "/Badge"}}
differences 21
   {"prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry", "attr": "extent", "change": "values", "max_abs_delta": 0.0025949478149414062, "elements_changed": 2, "elements": 2}
   {"prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry", "attr": "faceVertexCounts", "change": "array shape", "old": [230], "new": [98]}
   {"prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry", "attr": "faceVertexIndices", "change": "array shape", "old": [690], "new": [294]}
   {"prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry", "attr": "normals", "change": "array shape", "old": [690, 3], "new": [294, 3]}
   {"prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry", "attr": "points", "change": "array shape", "old": [117, 3], "new": [51, 3]}
   {"prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry", "attr": "primvars:USDZ_UV", "change": "array shape", "old": [170, 2], "new": [51, 2]}
   {"prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry", "attr": "primvars:USDZ_UV:indices", "change": "array shape", "old": [690], "new": [294]}
   {"prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry/Emblem___satin_silver_facets_Mobile_Emblem", "attr": "indices", "change": "array shape", "old": [180], "new": [34]}
   {"prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry/Emblem___shaded_outer_facets_Mobile_Emblem", "attr": "indices", "change": "array shape", "old": [50], "new": [64]}
   {"prim": "/Badge/_materials/Back_and_edge___gunmetal_Mobile_Casing/Image_Texture", "attr": "inputs:file", "change": "value", "old": "@./textures/USDZ_Casing_base_color.png@", "new": "@./textures/USDZ_Casing_back_base_color.png@"}
   {"prim": "/Badge/_materials/Back_and_edge___gunmetal_Mobile_Casing/Image_Texture_001", "attr": "inputs:file", "change": "value", "old": "@./textures/USDZ_Casing_roughness.png@", "new": "@./textures/USDZ_Casing_back_roughness.png@"}
   {"prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Principled_BSDF", "attr": "inputs:diffuseColor", "change": "values", "max_abs_delta": 0.20000001788139343, "elements_changed": 3, "elements": 3}
   {"prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Principled_BSDF", "attr": "inputs:diffuseColor", "change": "values", "max_abs_delta": 0.019999995827674866, "elements_changed": 3, "elements": 3}
   {"prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Image_Texture_001", "change": "removed", "type": "Shader"}
   {"prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Principled_BSDF", "attr": "inputs:normal", "change": "attribute removed"}
   {"prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/UV_Map_001", "change": "removed", "type": "Shader"}
   {"prim": "/Badge/_materials/Outer_edge___smooth_satin_silver_Mobile_Casing/Image_Texture", "attr": "inputs:file", "change": "value", "old": "@./textures/USDZ_Casing_base_color.png@", "new": "@./textures/USDZ_Casing_outer_base_color.png@"}
   {"prim": "/Badge/_materials/Outer_edge___smooth_satin_silver_Mobile_Casing/Image_Texture_001", "attr": "inputs:file", "change": "value", "old": "@./textures/USDZ_Casing_roughness.png@", "new": "@./textures/USDZ_Casing_outer_roughness.png@"}
   {"prim": "/Badge/_materials/Recess___smoked_nickel_Mobile_Inner_channel/Principled_BSDF", "attr": "inputs:diffuseColor", "change": "values", "max_abs_delta": 0.02499999850988388, "elements_changed": 3, "elements": 3}
   {"prim": "/Badge/_materials/Silver___polished_cut_edges_Mobile_Inner_edge/Principled_BSDF", "attr": "inputs:diffuseColor", "change": "values", "max_abs_delta": 0.3399999737739563, "elements_changed": 3, "elements": 3}
   {"prim": "/Badge/_materials/Silver___polished_cut_edges_Mobile_Rim_inner_lip/Principled_BSDF", "attr": "inputs:diffuseColor", "change": "values", "max_abs_delta": 0.3399999737739563, "elements_changed": 3, "elements": 3}
bounds identical: False
   /Badge [[-3.01487135887146, -2.8949999809265137, -0.3450004458427429], [3.01487135887146, 3.01487135887146, 0.9771202802658081]] -> [[-3.01487135887146, -2.8949999809265137, -0.3450004458427429], [3.01487135887146, 3.01487135887146, 0.974890410900116]]
   /Badge/Casing___smooth_rounded_outer_edge/Casing___smooth_rounded_outer_edge_mobile_geometry [[-3.01487135887146, -2.8949999809265137, -0.3450004458427429], [3.01487135887146, 3.01487135887146, 0.2600186765193939]] -> [[-3.01487135887146, -2.8949999809265137, -0.3450004458427429], [3.01487135887146, 3.01487135887146, 0.2600186765193939]]
   /Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry [[-1.0885751247406006, -2.0473744869232178, 0.11999999731779099], [1.0885751247406006, 2.017314910888672, 0.9771202802658081]] -> [[-1.0869446992874146, -2.0447795391082764, 0.11999981105327606], [1.0870530605316162, 2.0148818492889404, 0.974890410900116]]
   /Badge/Inner_channel___shadowed_bevel/Inner_channel___shadowed_bevel_mobile_geometry [[-2.6401007175445557, -2.6401007175445557, 0.01798584684729576], [2.6401007175445557, 2.6401007175445557, 0.20115379989147186]] -> [[-2.6401007175445557, -2.6401007175445557, 0.01798584684729576], [2.6401007175445557, 2.6401007175445557, 0.20115379989147186]]
   /Badge/Inner_edge___fine_silver_reveal/Inner_edge___fine_silver_reveal_mobile_geometry [[-2.5390655994415283, -2.5390655994415283, 0.06098673492670059], [2.5390655994415283, 2.5390655994415283, 0.09602090716362]] -> [[-2.5390655994415283, -2.5390655994415283, 0.06098673492670059], [2.5390655994415283, 2.5390655994415283, 0.09602090716362]]
   /Badge/Inset___charcoal_textured_disk/Inset___charcoal_textured_disk_mobile_geometry [[-2.5250000953674316, -2.5250000953674316, -0.13100045919418335], [2.5250000953674316, 2.5250000953674316, 0.03900047391653061]] -> [[-2.5250000953674316, -2.5250000953674316, -0.13100045919418335], [2.5250000953674316, 2.5250000953674316, 0.03900047391653061]]
   /Badge/Rim_inner_lip___narrow_highlight/Rim_inner_lip___narrow_highlight_mobile_geometry [[-2.6612191200256348, -2.6612191200256348, 0.18692268431186676], [2.6612191200256348, 2.6612191200256348, 0.22401870787143707]] -> [[-2.6612191200256348, -2.6612191200256348, 0.18692268431186676], [2.6612191200256348, 2.6612191200256348, 0.22401870787143707]]
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)

Blender quit

```

### proof/proof_analysis.txt

```text
/Users/antonioperedo/Downloads/badge_realitykit_iron/proof/emblem_stage_pose00.png (1764, 1838)
/Users/antonioperedo/Downloads/badge_realitykit_iron/proof/emblem_stage_pose20.png (1764, 1838)
/Users/antonioperedo/Downloads/badge_realitykit_iron/proof/emblem_harsh_pose00.png (1764, 1838)
/Users/antonioperedo/Downloads/badge_realitykit_iron/proof/emblem_harsh_pose20.png (1764, 1838)
/Users/antonioperedo/Downloads/badge_realitykit_iron/proof/ring_inset_stage_pose00.png (1164, 1598)
/Users/antonioperedo/Downloads/badge_realitykit_iron/proof/ring_inset_harsh_pose00.png (1164, 1598)
stage_pose00 gem: max 221 mean 33.1611 differing 127464/127600 | bottom_rim_above_floor: max 195 mean 20.9517 differing 22103/22400 | bottom_rim_with_floor_contact: max 195 mean 23.1881 differing 40977/44800 | whole_frame: max 221 mean 5.7911 differing 317559/1555200
stage_pose20 gem: max 231 mean 35.8844 differing 127425/127600 | bottom_rim_above_floor: max 72 mean 16.9489 differing 21401/22400 | bottom_rim_with_floor_contact: max 101 mean 16.2761 differing 37901/44800 | whole_frame: max 231 mean 5.6085 differing 284989/1555200
harsh_pose00 gem: max 227 mean 34.1523 differing 127431/127600 | bottom_rim_above_floor: max 215 mean 20.9451 differing 22196/22400 | bottom_rim_with_floor_contact: max 215 mean 22.6843 differing 41517/44800 | whole_frame: max 227 mean 5.7409 differing 317729/1555200
harsh_pose20 gem: max 234 mean 34.4168 differing 127379/127600 | bottom_rim_above_floor: max 96 mean 16.6741 differing 21436/22400 | bottom_rim_with_floor_contact: max 96 mean 15.7749 differing 37649/44800 | whole_frame: max 234 mean 5.3659 differing 284772/1555200
Proof sheets, individual facet/rim/inset crops, smoothness numbers, and uniform-texture verification complete.

```

### proof/smoothness_pose00.txt

```text
=== pose 0.0: per-facet rough (cubic residual RMS, luma levels)
                              g2     g0     g4    g15     g6    g13     g7     g9    g11   mean  mottle  grain
iron_stage                  0.28   0.38   0.26   0.32   0.25   0.27   0.19   0.27   0.31   0.28   0.35   0.23
iron_harsh                  0.28   0.48   0.28   0.28   0.25   0.27   0.17   0.26   0.36   0.29   0.32   0.22
                            edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain
iron_stage                   1.68 /  4.99        28.9 /  147.5         2.34 /  3.44       0.15            0.14
iron_harsh                   1.59 /  5.53        26.1 /  129.8         2.37 /  3.79       0.19            0.16

```

### proof/smoothness_pose20.txt

```text
=== pose 20.0: per-facet rough (cubic residual RMS, luma levels)
                              g1     g2     g0     g4    g15     g6     g7    g13     g9    g11   mean  mottle  grain
iron_stage                  0.62   0.29   0.34   0.43   0.54   0.29   1.05   0.63   0.37   0.82   0.54   0.36   0.25
iron_harsh                  0.62   0.23   0.44   0.50   0.56   0.29   1.29   0.61   0.33   0.86   0.57   0.37   0.25
                            edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain
iron_stage                   1.86 /  4.97        43.8 /  195.8         1.48 /  2.43       0.13            0.19
iron_harsh                   1.96 /  5.35        46.3 /  197.0         1.47 /  2.34       0.21            0.43

```

### proof/smoothness_pose45.txt

```text
=== pose 45.0: per-facet rough (cubic residual RMS, luma levels)
                              g1     g2     g0    g16    g15     g6    g14    g13     g9    g11   mean  mottle  grain
iron_harsh                  0.27   0.29   0.38   0.30   0.55   0.53   0.28   0.64   0.63   0.69   0.46   0.39   0.32
                            edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain
iron_harsh                   2.20 /  7.69        47.7 /  224.8         1.69 /   nan       0.17            0.74

```

### proof/smoothness_silver_pose00.txt

```text
=== pose 0.0: per-facet rough (cubic residual RMS, luma levels)
                              g0     g2     g1     g3     g9    g10     g6    g12     g8    g11   mean  mottle  grain
silver_stage                0.41   0.83   0.43   0.43   0.84   0.79   0.87   0.24   2.17   2.14   0.92   0.64   0.31
silver_harsh                0.43   0.64   0.32   0.33   0.68   0.76   1.03   0.25   2.42   3.12   1.00   0.68   0.32
                            edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain
silver_stage                 2.69 /  6.71        61.5 /  198.9         2.01 /  2.64       0.39            0.36
silver_harsh                 2.85 /  6.47        64.6 /  202.3         2.13 /  2.79       0.47            0.43

```

### proof/smoothness_silver_pose20.txt

```text
=== pose 20.0: per-facet rough (cubic residual RMS, luma levels)
                              g5     g0     g2     g3     g1    g11    g10     g9    g12     g6     g8   mean  mottle  grain
silver_stage                0.55   0.55   1.61   0.53   0.45   0.31   0.29   0.28   0.24   0.26   0.28   0.49   0.47   0.28
silver_harsh                0.51   0.32   2.10   0.57   0.33   0.44   0.23   0.26   0.29   0.26   0.27   0.51   0.48   0.27
                            edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain
silver_stage                 2.16 /  6.17        44.5 /  180.6         2.09 /  3.37       0.36            0.41
silver_harsh                 1.91 /  7.07        39.4 /  183.8         2.11 /  3.07       0.34            0.48

```

### proof/smoothness_no_denoise.txt

```text
=== pose 0.0: per-facet rough (cubic residual RMS, luma levels)
                              g2     g0     g4    g15     g6    g13     g7     g9    g11   mean  mottle  grain
iron_raw                    0.35   0.48   2.61   0.26   0.42   0.62   0.66   6.91   6.51   2.09   2.09   2.01
                            edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain
iron_raw                     2.39 /  5.58        26.6 /  129.6         2.50 /  3.73       0.27            0.27

```

### proof/smoothness_realtime.txt

```text
=== pose 0.0: per-facet rough (cubic residual RMS, luma levels)
                              g2     g0     g4    g15     g6    g13     g7     g9    g11   mean  mottle  grain
iron_realtime               0.20   0.46   0.21   0.22   0.23   0.21   0.19   0.06   0.23   0.22   0.29   0.19
                            edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain
iron_realtime                1.48 /  5.00        28.1 /  135.9         2.17 /  3.68       0.20            0.17

```

### proof/texture_uniformity.json

```json
{
  "USDZ_Casing_base_color.png": {
    "size": [
      512,
      512
    ],
    "unique_rgb_colors": 1,
    "rgb8": [
      108,
      105,
      99
    ]
  },
  "USDZ_Casing_back_roughness.png": {
    "size": [
      512,
      512
    ],
    "unique_rgb_colors": 1,
    "rgb8": [
      82,
      82,
      82
    ]
  },
  "USDZ_Inset_base_color.png": {
    "size": [
      512,
      512
    ],
    "unique_rgb_colors": 1,
    "rgb8": [
      24,
      25,
      27
    ]
  },
  "USDZ_Casing_back_base_color.png": {
    "size": [
      512,
      512
    ],
    "unique_rgb_colors": 1,
    "rgb8": [
      14,
      13,
      12
    ]
  },
  "USDZ_Casing_outer_base_color.png": {
    "size": [
      512,
      512
    ],
    "unique_rgb_colors": 1,
    "rgb8": [
      27,
      26,
      24
    ]
  },
  "USDZ_Casing_roughness.png": {
    "size": [
      512,
      512
    ],
    "unique_rgb_colors": 1,
    "rgb8": [
      83,
      83,
      83
    ]
  },
  "USDZ_Casing_outer_roughness.png": {
    "size": [
      512,
      512
    ],
    "unique_rgb_colors": 1,
    "rgb8": [
      69,
      69,
      69
    ]
  }
}
```

### proof/scene_and_normals_validation.json

```json
{
  "iron_badge_mobile_reduced": {
    "Casing | smooth rounded outer edge": {
      "mesh_name": "Casing | smooth rounded outer edge mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 26566,
      "identity_world_transform": true
    },
    "Emblem | faceted compass spear": {
      "mesh_name": "Emblem | faceted compass spear mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 98,
      "identity_world_transform": true
    },
    "Inner channel | shadowed bevel": {
      "mesh_name": "Inner channel | shadowed bevel mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 3500,
      "identity_world_transform": true
    },
    "Inner edge | fine silver reveal": {
      "mesh_name": "Inner edge | fine silver reveal mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 2200,
      "identity_world_transform": true
    },
    "Inset | charcoal textured disk": {
      "mesh_name": "Inset | charcoal textured disk mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 3570,
      "identity_world_transform": true
    },
    "Rim inner lip | narrow highlight": {
      "mesh_name": "Rim inner lip | narrow highlight mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 2500,
      "identity_world_transform": true
    }
  },
  "iron_badge_mobile": {
    "Casing | smooth rounded outer edge": {
      "mesh_name": "Casing | smooth rounded outer edge mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 26566,
      "identity_world_transform": true
    },
    "Emblem | faceted compass spear": {
      "mesh_name": "Emblem | faceted compass spear mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 98,
      "identity_world_transform": true,
      "broad_triangle_max_corner_normal_variation": 0.0
    },
    "Inner channel | shadowed bevel": {
      "mesh_name": "Inner channel | shadowed bevel mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 3500,
      "identity_world_transform": true
    },
    "Inner edge | fine silver reveal": {
      "mesh_name": "Inner edge | fine silver reveal mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 2200,
      "identity_world_transform": true
    },
    "Inset | charcoal textured disk": {
      "mesh_name": "Inset | charcoal textured disk mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 3570,
      "identity_world_transform": true
    },
    "Rim inner lip | narrow highlight": {
      "mesh_name": "Rim inner lip | narrow highlight mobile geometry",
      "points_exactly_equal_to_usdz": true,
      "triangles": 2500,
      "identity_world_transform": true
    }
  },
  "normal_map_connections": []
}
```

### proof/original_integrity.json

```json
{
  "original_files_checked": 105,
  "changed": [],
  "missing": [],
  "reference_copy_identical": true,
  "app_repo_modified": false
}
```

### render_proof.py outputs

All successful render logs are provided under logs/render_*.log. Each lists the six imported meshes and its RENDERED output path. All proof PNGs have been decoded successfully. Full per-facet and per-region numeric arrays are in proof/smoothness_*.json and proof/render_diff_silver_vs_iron.json. High-pass images were made only in separate proof sheets; original renders and the asset were not retouched.


## Final delivery check

```json
{
  "required_files_present": 9,
  "proof_pngs_decoded": 81,
  "embedded_textures_exactly_equal_to_delivered_pngs": 7,
  "usdz_zip_crc": "PASS",
  "original_files_unchanged": 105,
  "usdz_sha256": "b01852569a49fb62826c0b2e7266bb35ad01cac0de59dd6dbf0ef5f084b77575"
}
```
