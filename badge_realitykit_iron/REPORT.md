# Iron badge: smooth floor-contact band

The local Iron asset is corrected to follow badge AGENTS.md sections 2.5 and 5.7. Its forged casing textures fade out across the lowest 5% of the nominal coin height. The lowest 0.08 model units above the cut are completely even in color and roughness, with flattened tangent-space normal relief. The remaining 0.2215 units use a smooth transition back to the approved finish. This removes the textured rim band that could visually merge with its reflection. No dark line, floor, light or reflection has been baked into the asset. The app continues to supply the floor/contact shadow.

**Installed and verified in the app.** The owner explicitly approved replacing the project's already-modified badge asset and leaving corrected Iron installed. The exact delivered USDZ bytes were built, loaded and captured on the iPhone 17 simulator after shader warmup and two relaunches. Loaded 3D=True, emblem clipping=117 pixels (limit796), rim_top=145.1 (130..175), emblem_mean=84.9. Both implementation and independent parent inspection accept the targeted floor-contact fade: smoother lower rim and reflected rim, thin dark separator retained, no new seam, halo or framing shift. Crystal reflection shape is intentionally unchanged. App source and reflection code were not edited. The old uniform-surface smoothness criterion remains false under the authorized forged-texture policy.

The previous centered Iron is preserved in `previous/centered01/`. All historical revisions remain intact. The approved crystal shape, size, centering, color maps, roughness and normal maps are unchanged. The inset and mounting occlusion are unchanged. All object, mesh and material IDs remain identical to silver; no names were lost. All six meshes, custom normals, triangle data, UVs, bounds, transforms and material/shader properties are identical to the previous Iron. Only five embedded casing PNG maps changed. Outside the faded band, every texture pixel is exactly preserved. The gunmetal back maps remain byte-identical.

The casing, lip, inner edge, inner channel and inset retain the exact silver geometry. Floor cut is uncapped at Y=-2.895; USD is Y up, metersPerUnit=1, front +Z with identity transforms. Bevels and their owner normals/materials are unchanged. No widened bevel glints.

[Corrected USDZ](mobile/iron_badge_mobile.usdz), [front Blender proof](proof/iron_front_app_lighting.png), [three-quarter Blender proof](proof/iron_three_quarter_app_lighting.png), [silver comparison](proof/silver_vs_iron_same_scale.png), [floor contact: silver / before / after](proof/floor_contact_silver_before_after.png), [contact zoom](proof/floor_contact_after_zoom.png), [fade mask](proof/contact_fade_mask.png), [raw smoothness](proof/NUMBERS.md). These are Blender proofs, not screenshots from the app.

## Checks

| Check | Result |
|---|---|
| usdchecker --arkit | PASS |
| reimport_check.py | PASS |
| verify_floor_cut.py | PASS, uncapped -2.895 |
| compare_usd.py against silver | PASS, five frozen shell prims exact; all differences recorded |
| compare_usd.py against previous centered Iron | PASS, zero USD attribute differences |
| Plane flatness | PASS, maximum normal difference 0 for every plane |
| Reduced/final scenes and USD geometry | PASS, exact positions and triangle counts |
| Blender point-light brightness and neighbor tones | PASS |
| Texture scope | PASS, five casing maps changed; all outside-band pixels exact |
| USDZ CRC and embedded maps | PASS, 14 maps, all 512 x 512 |
| App loaded_3d / clipping / rim / targeted contact review | PASS: loaded=True, clip117, rim145.1, clean transition |

Intentional texture and restrained normal maps remain authorized by the owner's earlier reference-match request. The old uniform-surface residual limits are reported as historical diagnostics, not relabeled as passes. This correction changes only the contact-band finish; it does not claim the existing forged finish meets every new texture-scale rule. App visual inspection of this targeted correction is complete; texture residuals remain reported under the owner-authorized forged finish.

Local visual review: the native-pixel Blender contact comparison shows a smoother coin/reflection transition and retains the narrow dark gap, without a visible seam at the texture fade. A fixed lower-rim crop (x=510..570, y=926..937 in the 1080 x 1440 proof) has mean absolute sigma-1 high-pass residual 3.5163 before and 2.0429 after, about a 42% reduction. Silver in that crop is 0.9635. This is a local image diagnostic, supplementary to the actual app inspection and specified facet smoothness measurement.

## Budget

| Asset | Triangles | Bytes |
|---|---:|---:|
| Silver v3 | 38,566 | 3,511,448 |
| Previous centered Iron | 38,428 | 4,250,473 |
| Corrected Iron | 38,428 | 4,132,206 |

## Materials

All nominal linear RGB, metallic and roughness values are unchanged. Color and roughness maps become these constant values only in the contact region. Crystal maps, palette and plane gains remain exactly as approved.

| Material ID | Linear RGB | Metallic | Roughness |
|---|---|---:|---:|
| `Silver___circumferential_brushed_steel_Mobile_Casing` | (0.25, 0.24, 0.225) | 1 | 0.325 |
| `Outer_edge___smooth_satin_silver_Mobile_Casing` | (0.245, 0.235, 0.22) | 1 | 0.27 |
| `Back_and_edge___gunmetal_Mobile_Casing` | (0.055, 0.052, 0.048) | 0.95 | 0.32 |
| `Silver___polished_cut_edges_Mobile_Inner_edge` | (0.3, 0.285, 0.26) | 1 | 0.19 |
| `Silver___polished_cut_edges_Mobile_Rim_inner_lip` | (0.3, 0.285, 0.26) | 1 | 0.19 |
| `Emblem___satin_silver_facets_Mobile_Emblem` | (0.4, 0.387, 0.371) | 1 | 0.36 |
| `Emblem___shaded_outer_facets_Mobile_Emblem` | (0.295, 0.282, 0.265) | 1 | 0.4 |
| `Recess___smoked_nickel_Mobile_Inner_channel` | (0.045, 0.043, 0.039) | 1 | 0.27 |
| `Inset___finely_textured_charcoal_Mobile_Inset` | (0.0027, 0.003, 0.0033) | 0.05 | 0.83 |

## Raw outputs

### logs/full_verification_run.txt

```text
PASS geometry_identity.txt
PASS scene_and_normals_validation.txt
PASS crystal_design_validation.txt
PASS usd_diff_silver_vs_iron.txt
PASS usd_diff_previous_vs_iron.txt
PASS usd_diff_final08_vs_iron.txt
PASS usd_diff_forged05_vs_iron.txt
PASS reimport_check.txt
PASS floor_cut_verification.txt
PASS floor_cut_topology.txt
PASS proof_geometry.txt
PASS usdchecker --arkit

```

### proof/usdchecker.log

```text
Coding Error: in RegisterBehaviorForPrimTypeId at line 454 of usdShade/connectableAPIBehavior.cpp -- UsdShade Connectable behavior already registered for primTypeId comprised of 'Scope' type and apischemas.
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
MESH Emblem___faceted_compass_spear_mobile_geometry: 48 verts, 92 tris, custom normals True, UVs ['USDZ_UV'], local bounds min [-1.21831, -1.84856, 0.033] max [1.20213, 1.88657, 0.95827]
    material Emblem___shaded_outer_facets_Mobile_Emblem: 63 faces
    material Emblem___satin_silver_facets_Mobile_Emblem: 29 faces
MESH Inner_channel___shadowed_bevel_mobile_geometry: 1750 verts, 3500 tris, custom normals True, UVs ['Machining_UV'], local bounds min [-2.6401, -2.6401, 0.01799] max [2.6401, 2.6401, 0.20115]
    material Recess___smoked_nickel_Mobile_Inner_channel: 3500 faces
MESH Inner_edge___fine_silver_reveal_mobile_geometry: 1100 verts, 2200 tris, custom normals True, UVs ['Machining_UV'], local bounds min [-2.53907, -2.53907, 0.06099] max [2.53907, 2.53907, 0.09602]
    material Silver___polished_cut_edges_Mobile_Inner_edge: 2200 faces
MESH Inset___charcoal_textured_disk_mobile_geometry: 1787 verts, 3570 tris, custom normals True, UVs ['USDZ_UV', 'UVMap'], local bounds min [-2.525, -2.525, -0.131] max [2.525, 2.525, 0.039]
    material Inset___finely_textured_charcoal_Mobile_Inset: 3570 faces
MESH Rim_inner_lip___narrow_highlight_mobile_geometry: 1250 verts, 2500 tris, custom normals True, UVs ['Machining_UV'], local bounds min [-2.66122, -2.66122, 0.18692] max [2.66122, 2.66122, 0.22402]
    material Silver___polished_cut_edges_Mobile_Rim_inner_lip: 2500 faces
OBJECT _materials (EMPTY)
TOTAL TRIANGLES 38428
MATERIAL Back_and_edge___gunmetal_Mobile_Casing: base color texture, {'Metallic': 0.95}, linked inputs {'Base Color': 'TEX_IMAGE', 'Roughness': 'SEPARATE_COLOR'}, images ['USDZ_Casing_back_base_color.png', 'USDZ_Casing_back_roughness.png']
MATERIAL Emblem___satin_silver_facets_Mobile_Emblem: base color texture, {'Metallic': 1.0}, linked inputs {'Base Color': 'TEX_IMAGE', 'Roughness': 'SEPARATE_COLOR', 'Normal': 'NORMAL_MAP'}, images ['USDZ_Emblem_base_color.png', 'USDZ_Emblem_roughness.png', 'USDZ_Emblem_normal.png']
MATERIAL Emblem___shaded_outer_facets_Mobile_Emblem: base color texture, {'Metallic': 1.0}, linked inputs {'Base Color': 'TEX_IMAGE', 'Roughness': 'SEPARATE_COLOR', 'Normal': 'NORMAL_MAP'}, images ['USDZ_Emblem_shaded_base_color.png', 'USDZ_Emblem_roughness.png', 'USDZ_Emblem_normal.png']
MATERIAL Inset___finely_textured_charcoal_Mobile_Inset: base color texture, {'Metallic': 0.05}, linked inputs {'Base Color': 'TEX_IMAGE', 'Roughness': 'SEPARATE_COLOR', 'Normal': 'NORMAL_MAP'}, images ['USDZ_Inset_base_color.png', 'USDZ_Inset_roughness.png', 'USDZ_Inset_normal.png']
MATERIAL Outer_edge___smooth_satin_silver_Mobile_Casing: base color texture, {'Metallic': 1.0}, linked inputs {'Base Color': 'TEX_IMAGE', 'Roughness': 'SEPARATE_COLOR', 'Normal': 'NORMAL_MAP'}, images ['USDZ_Casing_outer_base_color.png', 'USDZ_Casing_outer_roughness.png', 'USDZ_Casing_normal.png']
MATERIAL Recess___smoked_nickel_Mobile_Inner_channel: base color (0.045, 0.043, 0.039), {'Metallic': 1.0, 'Roughness': 0.27}, linked inputs {}, images []
MATERIAL Silver___circumferential_brushed_steel_Mobile_Casing: base color texture, {'Metallic': 1.0}, linked inputs {'Base Color': 'TEX_IMAGE', 'Roughness': 'SEPARATE_COLOR', 'Normal': 'NORMAL_MAP'}, images ['USDZ_Casing_base_color.png', 'USDZ_Casing_roughness.png', 'USDZ_Casing_normal.png']
MATERIAL Silver___polished_cut_edges_Mobile_Inner_edge: base color (0.3, 0.285, 0.26), {'Metallic': 1.0, 'Roughness': 0.19}, linked inputs {}, images []
MATERIAL Silver___polished_cut_edges_Mobile_Rim_inner_lip: base color (0.3, 0.285, 0.26), {'Metallic': 1.0, 'Roughness': 0.19}, linked inputs {}, images []
IMAGE USDZ_Casing_back_base_color.png: 512x512, sRGB, packed True
IMAGE USDZ_Casing_back_roughness.png: 512x512, Non-Color, packed True
IMAGE USDZ_Casing_base_color.png: 512x512, sRGB, packed True
IMAGE USDZ_Casing_normal.png: 512x512, Non-Color, packed True
IMAGE USDZ_Casing_outer_base_color.png: 512x512, sRGB, packed True
IMAGE USDZ_Casing_outer_roughness.png: 512x512, Non-Color, packed True
IMAGE USDZ_Casing_roughness.png: 512x512, Non-Color, packed True
IMAGE USDZ_Emblem_base_color.png: 512x512, sRGB, packed True
IMAGE USDZ_Emblem_normal.png: 512x512, Non-Color, packed True
IMAGE USDZ_Emblem_roughness.png: 512x512, Non-Color, packed True
IMAGE USDZ_Emblem_shaded_base_color.png: 512x512, sRGB, packed True
IMAGE USDZ_Inset_base_color.png: 512x512, sRGB, packed True
IMAGE USDZ_Inset_normal.png: 512x512, Non-Color, packed True
IMAGE USDZ_Inset_roughness.png: 512x512, Non-Color, packed True
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)
USD import of '/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/floor_contact_revision/01/mobile/iron_badge_mobile.usdz' took 98.30 ms

Blender quit

```

### proof/floor_cut_verification.txt

```text
{
 "uncut": "/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/floor_contact_revision/01/work/iron_uncut.usdz",
 "cut": "/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/floor_contact_revision/01/mobile/iron_badge_mobile.usdz",
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
   "min_y_uncut": -1.8485580682754517,
   "min_y_cut": -1.8485580682754517,
   "max_uncut": [
    1.2021337747573853,
    1.8865662813186646,
    0.9582700133323669
   ],
   "max_cut": [
    1.2021337747573853,
    1.8865662813186646,
    0.9582700133323669
   ],
   "triangles_uncut": 92,
   "triangles_cut": 92,
   "byte_identical": true,
   "sha1_uncut": "15612e97cd6f5ea0fbd32c634d4f8272aeb8cb5d",
   "sha1_cut": "15612e97cd6f5ea0fbd32c634d4f8272aeb8cb5d"
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
01 edges 39954 boundary 210 on floor 210 non-manifold 0 points 13389 unique positions 13389
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)

Blender quit

```

### proof/geometry_identity.txt

```text
00:01.816  blend            | Read blend: "/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/floor_contact_revision/01/scenes/iron_medallion_master.blend"
PASS: all five enclosure meshes exact; all six mesh and nine material names exact; Y-up/meters/identity transforms/floor correct; master enclosure unchanged
{
  "total_triangles_silver": 38566,
  "total_triangles_iron": 38428,
  "bytes_silver": 3511448,
  "bytes_iron": 4132206
}
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)

Blender quit

```

### proof/scene_and_normals_validation.txt

```text
00:00.654  blend            | Read blend: "/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/floor_contact_revision/01/scenes/iron_badge_mobile_reduced.blend"
00:00.722  blend            | Read blend: "/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/floor_contact_revision/01/scenes/iron_badge_mobile.blend"
PASS: reduced/final scene mesh positions and triangles match USDZ; broad facet corner normals are constant; five normal-map shader connections, all explicitly authorized for the forged finish.
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)

Blender quit

```

### proof/crystal_design_validation.txt

```text
00:00.598  blend            | Read blend: "/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/floor_contact_revision/01/scenes/iron_medallion_master.blend"
/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/floor_contact_revision/01/scripts/verify_crystal.py:31: DeprecationWarning: Arrays of 2-dimensional vectors are deprecated. Use arrays of 3-dimensional vectors instead. (deprecated in NumPy 2.0)
  ridge_error=max(float(abs(np.cross(delta,p[i,:2]-a))/np.linalg.norm(delta)) for i in ridge)
{
  "distinct_front_planes_at_one_degree": 6,
  "front_quads": 3,
  "front_tip_triangles": 3,
  "minimum_adjacent_crease_degrees": 15.91045685211862,
  "ridge_vertex_indices": [
    0,
    7,
    8,
    4
  ],
  "ridge_edges_all_shared_by_left_and_right_front_planes": true,
  "projected_ridge_line_max_deviation_units": 0.0,
  "analytic_front_planarity_max_deviation_units": 1.1102230246251565e-16,
  "all_master_crystal_polygons_flat_shaded": true,
  "front_plane_normal_vectors": [
    [
      -0.4742000102996826,
      0.3274533152580261,
      0.8172567486763
    ],
    [
      -0.4226759672164917,
      -0.06344262510538101,
      0.9040575623512268
    ],
    [
      -0.17387954890727997,
      -0.24432727694511414,
      0.9539759159088135
    ],
    [
      0.49866995215415955,
      0.3223856985569,
      0.8046090006828308
    ],
    [
      0.4317660927772522,
      -0.06314194947481155,
      0.8997728228569031
    ],
    [
      0.22495689988136292,
      -0.2417474091053009,
      0.943902850151062
    ]
  ],
  "left_main_right_shaded_materials": true,
  "maximum_normal_difference_within_any_plane": 0.0,
  "maximum_normal_angle_within_any_plane_degrees": 0.0,
  "final_broad_plane_geometry_max_deviation_units": 2.1234667176808795e-07,
  "planes": [
    {
      "plane": 0,
      "kind": "front_main",
      "broad_triangles": 1,
      "triangles_including_folded_strips": 3,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 1.0507858139163773e-07,
      "normal": [
        -0.4742000102996826,
        0.3274533152580261,
        0.8172567486763
      ],
      "phone_panel_area_pixels_at_320px_badge": 2404.2285738232313,
      "phone_panel_2area_over_perimeter_pixels": 19.25720997869609
    },
    {
      "plane": 1,
      "kind": "front_main",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 4,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 1.2714912633882136e-07,
      "normal": [
        -0.4226759672164917,
        -0.06344262510538101,
        0.9040575623512268
      ],
      "phone_panel_area_pixels_at_320px_badge": 4279.035661329108,
      "phone_panel_2area_over_perimeter_pixels": 30.040022502172587
    },
    {
      "plane": 2,
      "kind": "front_main",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 3,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 5.386231283210918e-08,
      "normal": [
        -0.17387954890727997,
        -0.24432727694511414,
        0.9539759159088135
      ],
      "phone_panel_area_pixels_at_320px_badge": 1030.5474639676395,
      "phone_panel_2area_over_perimeter_pixels": 13.075514223601752
    },
    {
      "plane": 3,
      "kind": "front_shaded",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 7,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 1.177740138746941e-07,
      "normal": [
        0.49866995215415955,
        0.3223856985569,
        0.8046090006828308
      ],
      "phone_panel_area_pixels_at_320px_badge": 3437.1161366014567,
      "phone_panel_2area_over_perimeter_pixels": 26.428490323818792
    },
    {
      "plane": 4,
      "kind": "front_shaded",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 4,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 1.4381695090381896e-07,
      "normal": [
        0.4317660927772522,
        -0.06314194947481155,
        0.8997728228569031
      ],
      "phone_panel_area_pixels_at_320px_badge": 4042.873890893534,
      "phone_panel_2area_over_perimeter_pixels": 29.75039903047635
    },
    {
      "plane": 5,
      "kind": "front_shaded",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 4,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 1.0085905088885738e-07,
      "normal": [
        0.22495689988136292,
        -0.2417474091053009,
        0.943902850151062
      ],
      "phone_panel_area_pixels_at_320px_badge": 1065.199518282956,
      "phone_panel_2area_over_perimeter_pixels": 13.523047592387904
    },
    {
      "plane": 6,
      "kind": "side_wall",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 7,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 6.082525660922045e-08,
      "normal": [
        0.45819661021232605,
        0.8888508677482605,
        0.0
      ]
    },
    {
      "plane": 7,
      "kind": "side_wall",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 6,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 1.246077414585045e-07,
      "normal": [
        0.9294254779815674,
        0.3690098226070404,
        0.0
      ]
    },
    {
      "plane": 8,
      "kind": "side_wall",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 7,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 9.615365570425638e-08,
      "normal": [
        0.9369000196456909,
        -0.3495972752571106,
        0.0
      ]
    },
    {
      "plane": 9,
      "kind": "side_wall",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 7,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 5.6992789265741806e-08,
      "normal": [
        0.5822826027870178,
        -0.812986433506012,
        0.0
      ]
    },
    {
      "plane": 10,
      "kind": "side_wall",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 6,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 1.1461381266286708e-07,
      "normal": [
        -0.4807218313217163,
        -0.8768730759620667,
        0.0
      ]
    },
    {
      "plane": 11,
      "kind": "side_wall",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 7,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 1.4626259936534325e-07,
      "normal": [
        -0.9451996684074402,
        -0.32649311423301697,
        0.0
      ]
    },
    {
      "plane": 12,
      "kind": "side_wall",
      "broad_triangles": 2,
      "triangles_including_folded_strips": 8,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 7.116211708790843e-08,
      "normal": [
        -0.8042200207710266,
        0.5943315625190735,
        0.0
      ]
    },
    {
      "plane": 13,
      "kind": "back",
      "broad_triangles": 5,
      "triangles_including_folded_strips": 19,
      "maximum_normal_component_difference": 0.0,
      "maximum_normal_angle_degrees": 0.0,
      "final_broad_plane_geometry_max_deviation_units": 2.1234667176808795e-07,
      "normal": [
        -1.1469389882279302e-09,
        0.0,
        -1.0
      ]
    }
  ]
}
PASS: six broad panels around a continuous centered ridge; normal difference exactly 0 within all front, side and back planes.
Blender 5.2.2 LTS (hash d13f752e3b9c built 2026-09-15 01:49:19)

Blender quit

```

### proof/usd_diff_centered_vs_contact.json

```text
{
  "old": "badge_realitykit_iron/centering_revision/01/mobile/iron_badge_mobile.usdz",
  "new": "badge_realitykit_iron/floor_contact_revision/01/mobile/iron_badge_mobile.usdz",
  "stage": {
    "old": {
      "upAxis": "Y",
      "metersPerUnit": 1.0,
      "defaultPrim": "/Badge"
    },
    "new": {
      "upAxis": "Y",
      "metersPerUnit": 1.0,
      "defaultPrim": "/Badge"
    }
  },
  "differences": [],
  "bounds_old": {
    "/Badge": [
      [
        -3.01487135887146,
        -2.8949999809265137,
        -0.3450004458427429
      ],
      [
        3.01487135887146,
        3.01487135887146,
        0.9582700133323669
      ]
    ],
    "/Badge/Inset___charcoal_textured_disk/Inset___charcoal_textured_disk_mobile_geometry": [
      [
        -2.5250000953674316,
        -2.5250000953674316,
        -0.13100045919418335
      ],
      [
        2.5250000953674316,
        2.5250000953674316,
        0.03900047391653061
      ]
    ],
    "/Badge/Inner_edge___fine_silver_reveal/Inner_edge___fine_silver_reveal_mobile_geometry": [
      [
        -2.5390655994415283,
        -2.5390655994415283,
        0.06098673492670059
      ],
      [
        2.5390655994415283,
        2.5390655994415283,
        0.09602090716362
      ]
    ],
    "/Badge/Casing___smooth_rounded_outer_edge/Casing___smooth_rounded_outer_edge_mobile_geometry": [
      [
        -3.01487135887146,
        -2.8949999809265137,
        -0.3450004458427429
      ],
      [
        3.01487135887146,
        3.01487135887146,
        0.2600186765193939
      ]
    ],
    "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry": [
      [
        -1.2183070182800293,
        -1.8485580682754517,
        0.03299978747963905
      ],
      [
        1.2021337747573853,
        1.8865662813186646,
        0.9582700133323669
      ]
    ],
    "/Badge/Inner_channel___shadowed_bevel/Inner_channel___shadowed_bevel_mobile_geometry": [
      [
        -2.6401007175445557,
        -2.6401007175445557,
        0.01798584684729576
      ],
      [
        2.6401007175445557,
        2.6401007175445557,
        0.20115379989147186
      ]
    ],
    "/Badge/Rim_inner_lip___narrow_highlight/Rim_inner_lip___narrow_highlight_mobile_geometry": [
      [
        -2.6612191200256348,
        -2.6612191200256348,
        0.18692268431186676
      ],
      [
        2.6612191200256348,
        2.6612191200256348,
        0.22401870787143707
      ]
    ]
  },
  "bounds_new": {
    "/Badge": [
      [
        -3.01487135887146,
        -2.8949999809265137,
        -0.3450004458427429
      ],
      [
        3.01487135887146,
        3.01487135887146,
        0.9582700133323669
      ]
    ],
    "/Badge/Inset___charcoal_textured_disk/Inset___charcoal_textured_disk_mobile_geometry": [
      [
        -2.5250000953674316,
        -2.5250000953674316,
        -0.13100045919418335
      ],
      [
        2.5250000953674316,
        2.5250000953674316,
        0.03900047391653061
      ]
    ],
    "/Badge/Inner_edge___fine_silver_reveal/Inner_edge___fine_silver_reveal_mobile_geometry": [
      [
        -2.5390655994415283,
        -2.5390655994415283,
        0.06098673492670059
      ],
      [
        2.5390655994415283,
        2.5390655994415283,
        0.09602090716362
      ]
    ],
    "/Badge/Casing___smooth_rounded_outer_edge/Casing___smooth_rounded_outer_edge_mobile_geometry": [
      [
        -3.01487135887146,
        -2.8949999809265137,
        -0.3450004458427429
      ],
      [
        3.01487135887146,
        3.01487135887146,
        0.2600186765193939
      ]
    ],
    "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry": [
      [
        -1.2183070182800293,
        -1.8485580682754517,
        0.03299978747963905
      ],
      [
        1.2021337747573853,
        1.8865662813186646,
        0.9582700133323669
      ]
    ],
    "/Badge/Inner_channel___shadowed_bevel/Inner_channel___shadowed_bevel_mobile_geometry": [
      [
        -2.6401007175445557,
        -2.6401007175445557,
        0.01798584684729576
      ],
      [
        2.6401007175445557,
        2.6401007175445557,
        0.20115379989147186
      ]
    ],
    "/Badge/Rim_inner_lip___narrow_highlight/Rim_inner_lip___narrow_highlight_mobile_geometry": [
      [
        -2.6612191200256348,
        -2.6612191200256348,
        0.18692268431186676
      ],
      [
        2.6612191200256348,
        2.6612191200256348,
        0.22401870787143707
      ]
    ]
  }
}
```

### proof/usd_diff_silver_vs_iron.json

```text
{
  "old": "/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/floor_contact_revision/01/source/silver_v3/silver_badge_mobile.usdz",
  "new": "/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/floor_contact_revision/01/mobile/iron_badge_mobile.usdz",
  "stage": {
    "old": {
      "upAxis": "Y",
      "metersPerUnit": 1.0,
      "defaultPrim": "/Badge"
    },
    "new": {
      "upAxis": "Y",
      "metersPerUnit": 1.0,
      "defaultPrim": "/Badge"
    }
  },
  "differences": [
    {
      "prim": "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry",
      "attr": "extent",
      "change": "values",
      "max_abs_delta": 0.1988164186477661,
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
        92
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
        276
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
        276,
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
        48,
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
        48,
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
        276
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
        29
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
        63
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
      "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Image_Texture",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Image_Texture_001",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Image_Texture_002",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Principled_BSDF",
      "attr": "inputs:diffuseColor",
      "change": "connection/interpolation",
      "old": [
        [],
        null
      ],
      "new": [
        [
          "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Image_Texture.outputs:rgb"
        ],
        null
      ]
    },
    {
      "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Principled_BSDF",
      "attr": "inputs:diffuseColor",
      "change": "array shape",
      "old": [
        3
      ],
      "new": []
    },
    {
      "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Principled_BSDF",
      "attr": "inputs:normal",
      "change": "attribute added",
      "new": "None"
    },
    {
      "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Principled_BSDF",
      "attr": "inputs:roughness",
      "change": "connection/interpolation",
      "old": [
        [],
        null
      ],
      "new": [
        [
          "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/Image_Texture_001.outputs:r"
        ],
        null
      ]
    },
    {
      "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/UV_Map",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/UV_Map_001",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___satin_silver_facets_Mobile_Emblem/UV_Map_002",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Image_Texture",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Image_Texture_001",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Image_Texture_002",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Principled_BSDF",
      "attr": "inputs:diffuseColor",
      "change": "connection/interpolation",
      "old": [
        [],
        null
      ],
      "new": [
        [
          "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Image_Texture.outputs:rgb"
        ],
        null
      ]
    },
    {
      "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Principled_BSDF",
      "attr": "inputs:diffuseColor",
      "change": "array shape",
      "old": [
        3
      ],
      "new": []
    },
    {
      "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Principled_BSDF",
      "attr": "inputs:normal",
      "change": "attribute added",
      "new": "None"
    },
    {
      "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Principled_BSDF",
      "attr": "inputs:roughness",
      "change": "connection/interpolation",
      "old": [
        [],
        null
      ],
      "new": [
        [
          "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/Image_Texture_001.outputs:r"
        ],
        null
      ]
    },
    {
      "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/UV_Map",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/UV_Map_001",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Emblem___shaded_outer_facets_Mobile_Emblem/UV_Map_002",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Image_Texture_001",
      "attr": "inputs:bias",
      "change": "attribute removed"
    },
    {
      "prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Image_Texture_001",
      "attr": "inputs:file",
      "change": "value",
      "old": "@./textures/USDZ_Inset_normal.png@",
      "new": "@./textures/USDZ_Inset_roughness.png@"
    },
    {
      "prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Image_Texture_001",
      "attr": "inputs:scale",
      "change": "attribute removed"
    },
    {
      "prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Image_Texture_002",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Principled_BSDF",
      "attr": "inputs:normal",
      "change": "connection/interpolation",
      "old": [
        [
          "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Image_Texture_001.outputs:rgb"
        ],
        null
      ],
      "new": [
        [
          "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Image_Texture_002.outputs:rgb"
        ],
        null
      ]
    },
    {
      "prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Principled_BSDF",
      "attr": "inputs:roughness",
      "change": "connection/interpolation",
      "old": [
        [],
        null
      ],
      "new": [
        [
          "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/Image_Texture_001.outputs:r"
        ],
        null
      ]
    },
    {
      "prim": "/Badge/_materials/Inset___finely_textured_charcoal_Mobile_Inset/UV_Map_002",
      "change": "added",
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
      "prim": "/Badge/_materials/Outer_edge___smooth_satin_silver_Mobile_Casing/Image_Texture_002",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Outer_edge___smooth_satin_silver_Mobile_Casing/Principled_BSDF",
      "attr": "inputs:normal",
      "change": "attribute added",
      "new": "None"
    },
    {
      "prim": "/Badge/_materials/Outer_edge___smooth_satin_silver_Mobile_Casing/UV_Map_002",
      "change": "added",
      "type": "Shader"
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
      "prim": "/Badge/_materials/Silver___circumferential_brushed_steel_Mobile_Casing/Image_Texture_002",
      "change": "added",
      "type": "Shader"
    },
    {
      "prim": "/Badge/_materials/Silver___circumferential_brushed_steel_Mobile_Casing/Principled_BSDF",
      "attr": "inputs:normal",
      "change": "attribute added",
      "new": "None"
    },
    {
      "prim": "/Badge/_materials/Silver___circumferential_brushed_steel_Mobile_Casing/UV_Map_002",
      "change": "added",
      "type": "Shader"
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
  ],
  "bounds_old": {
    "/Badge": [
      [
        -3.01487135887146,
        -2.8949999809265137,
        -0.3450004458427429
      ],
      [
        3.01487135887146,
        3.01487135887146,
        0.9771202802658081
      ]
    ],
    "/Badge/Inset___charcoal_textured_disk/Inset___charcoal_textured_disk_mobile_geometry": [
      [
        -2.5250000953674316,
        -2.5250000953674316,
        -0.13100045919418335
      ],
      [
        2.5250000953674316,
        2.5250000953674316,
        0.03900047391653061
      ]
    ],
    "/Badge/Inner_edge___fine_silver_reveal/Inner_edge___fine_silver_reveal_mobile_geometry": [
      [
        -2.5390655994415283,
        -2.5390655994415283,
        0.06098673492670059
      ],
      [
        2.5390655994415283,
        2.5390655994415283,
        0.09602090716362
      ]
    ],
    "/Badge/Casing___smooth_rounded_outer_edge/Casing___smooth_rounded_outer_edge_mobile_geometry": [
      [
        -3.01487135887146,
        -2.8949999809265137,
        -0.3450004458427429
      ],
      [
        3.01487135887146,
        3.01487135887146,
        0.2600186765193939
      ]
    ],
    "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry": [
      [
        -1.0885751247406006,
        -2.0473744869232178,
        0.11999999731779099
      ],
      [
        1.0885751247406006,
        2.017314910888672,
        0.9771202802658081
      ]
    ],
    "/Badge/Inner_channel___shadowed_bevel/Inner_channel___shadowed_bevel_mobile_geometry": [
      [
        -2.6401007175445557,
        -2.6401007175445557,
        0.01798584684729576
      ],
      [
        2.6401007175445557,
        2.6401007175445557,
        0.20115379989147186
      ]
    ],
    "/Badge/Rim_inner_lip___narrow_highlight/Rim_inner_lip___narrow_highlight_mobile_geometry": [
      [
        -2.6612191200256348,
        -2.6612191200256348,
        0.18692268431186676
      ],
      [
        2.6612191200256348,
        2.6612191200256348,
        0.22401870787143707
      ]
    ]
  },
  "bounds_new": {
    "/Badge": [
      [
        -3.01487135887146,
        -2.8949999809265137,
        -0.3450004458427429
      ],
      [
        3.01487135887146,
        3.01487135887146,
        0.9582700133323669
      ]
    ],
    "/Badge/Inset___charcoal_textured_disk/Inset___charcoal_textured_disk_mobile_geometry": [
      [
        -2.5250000953674316,
        -2.5250000953674316,
        -0.13100045919418335
      ],
      [
        2.5250000953674316,
        2.5250000953674316,
        0.03900047391653061
      ]
    ],
    "/Badge/Inner_edge___fine_silver_reveal/Inner_edge___fine_silver_reveal_mobile_geometry": [
      [
        -2.5390655994415283,
        -2.5390655994415283,
        0.06098673492670059
      ],
      [
        2.5390655994415283,
        2.5390655994415283,
        0.09602090716362
      ]
    ],
    "/Badge/Casing___smooth_rounded_outer_edge/Casing___smooth_rounded_outer_edge_mobile_geometry": [
      [
        -3.01487135887146,
        -2.8949999809265137,
        -0.3450004458427429
      ],
      [
        3.01487135887146,
        3.01487135887146,
        0.2600186765193939
      ]
    ],
    "/Badge/Emblem___faceted_compass_spear/Emblem___faceted_compass_spear_mobile_geometry": [
      [
        -1.2183070182800293,
        -1.8485580682754517,
        0.03299978747963905
      ],
      [
        1.2021337747573853,
        1.8865662813186646,
        0.9582700133323669
      ]
    ],
    "/Badge/Inner_channel___shadowed_bevel/Inner_channel___shadowed_bevel_mobile_geometry": [
      [
        -2.6401007175445557,
        -2.6401007175445557,
        0.01798584684729576
      ],
      [
        2.6401007175445557,
        2.6401007175445557,
        0.20115379989147186
      ]
    ],
    "/Badge/Rim_inner_lip___narrow_highlight/Rim_inner_lip___narrow_highlight_mobile_geometry": [
      [
        -2.6612191200256348,
        -2.6612191200256348,
        0.18692268431186676
      ],
      [
        2.6612191200256348,
        2.6612191200256348,
        0.22401870787143707
      ]
    ]
  }
}
```

### reports/contact_fade.json

```text
{
  "floor_y": -2.895,
  "fully_smooth_through_y": -2.815,
  "fade_ends_at_y": -2.5935,
  "band_height_units": 0.3014999999999999,
  "uv_overlap_max_height_difference": 0.010128554032004411,
  "uv_padding_texels": 2,
  "geometry_changed": false,
  "material_constants_changed": false,
  "app_source_changed": false,
  "textures": {
    "USDZ_Casing_base_color.png": {
      "changed_texels": 4734,
      "unchanged_outside_band": true,
      "previous_sha256": "ce4142643c29abbc69cb7547759031fad95fccd9e3e9c802cfeaed09b8750bd6",
      "new_sha256": "98d6790f335963dee1f8d8fe57f20f3c8015c62431f4232c0f22c150e3c54212",
      "smooth_target": [
        "color",
        [
          0.25,
          0.24,
          0.225
        ]
      ],
      "fully_smooth_region_unique_rgb": [
        [
          137,
          134,
          130
        ]
      ]
    },
    "USDZ_Casing_back_roughness.png": {
      "changed_texels": 0,
      "unchanged_outside_band": true,
      "previous_sha256": "732a278806110b4e25f32b09915a262928ba078ca86387962f03dae4b827e65e",
      "new_sha256": "732a278806110b4e25f32b09915a262928ba078ca86387962f03dae4b827e65e",
      "smooth_target": [
        "roughness",
        [
          0.32,
          0.32,
          0.32
        ]
      ],
      "fully_smooth_region_unique_rgb": [
        [
          82,
          82,
          82
        ]
      ]
    },
    "USDZ_Emblem_shaded_base_color.png": {
      "changed_texels": 0,
      "unchanged_outside_band": true,
      "previous_sha256": "1d79c74e1860cde1555e89126d5056f3ec01800153823051154d5bee55592036",
      "new_sha256": "1d79c74e1860cde1555e89126d5056f3ec01800153823051154d5bee55592036",
      "smooth_target": null
    },
    "USDZ_Inset_base_color.png": {
      "changed_texels": 0,
      "unchanged_outside_band": true,
      "previous_sha256": "2c0879f9dab087b8e73d6bbd9f2bd9bcb5e32455f3f35f2787da3dc0425da1e4",
      "new_sha256": "2c0879f9dab087b8e73d6bbd9f2bd9bcb5e32455f3f35f2787da3dc0425da1e4",
      "smooth_target": null
    },
    "USDZ_Casing_back_base_color.png": {
      "changed_texels": 0,
      "unchanged_outside_band": true,
      "previous_sha256": "89697c540139deff4a91cc851b3c7bfc256d03e0dd3dbb81944c10baf67c9c6a",
      "new_sha256": "89697c540139deff4a91cc851b3c7bfc256d03e0dd3dbb81944c10baf67c9c6a",
      "smooth_target": [
        "color",
        [
          0.055,
          0.052,
          0.048
        ]
      ],
      "fully_smooth_region_unique_rgb": [
        [
          66,
          64,
          62
        ]
      ]
    },
    "USDZ_Inset_roughness.png": {
      "changed_texels": 0,
      "unchanged_outside_band": true,
      "previous_sha256": "2134b7cfb73dc2c1701aa88259bc5454966125cde2ac5816e167a1c9ce745d45",
      "new_sha256": "2134b7cfb73dc2c1701aa88259bc5454966125cde2ac5816e167a1c9ce745d45",
      "smooth_target": null
    },
    "USDZ_Inset_normal.png": {
      "changed_texels": 0,
      "unchanged_outside_band": true,
      "previous_sha256": "841c925176b72bc6e05c3a8dcb209b0a7d62bd105f653c8adb6e70b0f7b8d92f",
      "new_sha256": "841c925176b72bc6e05c3a8dcb209b0a7d62bd105f653c8adb6e70b0f7b8d92f",
      "smooth_target": null
    },
    "USDZ_Casing_normal.png": {
      "changed_texels": 2519,
      "unchanged_outside_band": true,
      "previous_sha256": "0d14d4c081c637f70fb6ca21fc71019a5937a82c91fb64a2f1aa6772f47ecea9",
      "new_sha256": "2bfd4445ede729e4361806dcdb43978473a1cd0e8fa3575f704453eedf97679e",
      "smooth_target": [
        "normal",
        [
          0,
          0,
          1
        ]
      ],
      "fully_smooth_region_unique_rgb": [
        [
          128,
          128,
          255
        ]
      ]
    },
    "USDZ_Emblem_roughness.png": {
      "changed_texels": 0,
      "unchanged_outside_band": true,
      "previous_sha256": "cd5e0588337d5b5cd7ee5581ddabba5051d747556e8f8184667c1b64a79f93cc",
      "new_sha256": "cd5e0588337d5b5cd7ee5581ddabba5051d747556e8f8184667c1b64a79f93cc",
      "smooth_target": null
    },
    "USDZ_Emblem_base_color.png": {
      "changed_texels": 0,
      "unchanged_outside_band": true,
      "previous_sha256": "4c18ab5b8597f310135516fb2386b8b3403923f84ffa518a448c015de3a19a67",
      "new_sha256": "4c18ab5b8597f310135516fb2386b8b3403923f84ffa518a448c015de3a19a67",
      "smooth_target": null
    },
    "USDZ_Casing_outer_base_color.png": {
      "changed_texels": 4729,
      "unchanged_outside_band": true,
      "previous_sha256": "8e0a3a0d1f38b32d196163f678f951c77914d4e321526bf2f8752483261cc400",
      "new_sha256": "854076c9f05c1892f61483b3f3bf0110cd6aa18eed7f16d155bc20f4ba198a69",
      "smooth_target": [
        "color",
        [
          0.245,
          0.235,
          0.22
        ]
      ],
      "fully_smooth_region_unique_rgb": [
        [
          136,
          133,
          129
        ]
      ]
    },
    "USDZ_Emblem_normal.png": {
      "changed_texels": 0,
      "unchanged_outside_band": true,
      "previous_sha256": "0a81473b3ec760b77e6d17dde58af74793fed02c3b3b05ab95f80615d3d12152",
      "new_sha256": "0a81473b3ec760b77e6d17dde58af74793fed02c3b3b05ab95f80615d3d12152",
      "smooth_target": null
    },
    "USDZ_Casing_roughness.png": {
      "changed_texels": 4334,
      "unchanged_outside_band": true,
      "previous_sha256": "2caff3a210138f9257c55e8c39ceffe9e3ff9d303e5f7fdc97c6f625408c2e2d",
      "new_sha256": "32cd43598e728c8d9d0ac668024b62a8f00ab7c5691f214ada532942097188a7",
      "smooth_target": [
        "roughness",
        [
          0.325,
          0.325,
          0.325
        ]
      ],
      "fully_smooth_region_unique_rgb": [
        [
          83,
          83,
          83
        ]
      ]
    },
    "USDZ_Casing_outer_roughness.png": {
      "changed_texels": 4570,
      "unchanged_outside_band": true,
      "previous_sha256": "d6fb04918a06c17ee77f07c51567b25dd6efa0b11feba34cb6ccdc781a81ea67",
      "new_sha256": "cbf9c233a7ae48f6ca1ac27b8d30b90b8c9dcee6a69fa762c225fc9534619b8c",
      "smooth_target": [
        "roughness",
        [
          0.27,
          0.27,
          0.27
        ]
      ],
      "fully_smooth_region_unique_rgb": [
        [
          69,
          69,
          69
        ]
      ]
    }
  }
}

```

### proof/contact_render_metrics.json

```text
{
  "proof_type": "Blender app point-light rig, not an app screenshot",
  "rim_box": [
    510,
    926,
    570,
    937
  ],
  "high_pass_sigma": 1.0,
  "rows": {
    "silver": {
      "mean_luma": 181.69666484848483,
      "high_pass_mean": 0.9634745894826751,
      "high_pass_95": 6.574318346278724
    },
    "iron_before": {
      "mean_luma": 160.38432909090906,
      "high_pass_mean": 3.516345053116252,
      "high_pass_95": 10.18436475517335
    },
    "iron_after": {
      "mean_luma": 163.15975363636363,
      "high_pass_mean": 2.0429478201769284,
      "high_pass_95": 8.383728328193484
    }
  }
}

```

### blender_metrics.txt

```text
{
  "mask_method": "Blender-emitted scene-linear polygon IDs, full coverage only, eroded 3 pixels; all front panels required; visible side walls with at least 250 eroded pixels included",
  "neighbor_minimum_display_levels": 10,
  "front_plane_rows": {
    "stage": [
      {
        "plane": 0,
        "kind": "front_main",
        "pixels": 6513,
        "mean_luma": 212.0958665131276,
        "max_rgb": 243.0
      },
      {
        "plane": 1,
        "kind": "front_main",
        "pixels": 12659,
        "mean_luma": 130.37026787265975,
        "max_rgb": 206.0
      },
      {
        "plane": 2,
        "kind": "front_main",
        "pixels": 2481,
        "mean_luma": 179.75115977428456,
        "max_rgb": 236.0
      },
      {
        "plane": 3,
        "kind": "front_shaded",
        "pixels": 9908,
        "mean_luma": 127.04858362939038,
        "max_rgb": 209.0
      },
      {
        "plane": 4,
        "kind": "front_shaded",
        "pixels": 11957,
        "mean_luma": 77.88113978422682,
        "max_rgb": 165.0
      },
      {
        "plane": 5,
        "kind": "front_shaded",
        "pixels": 2555,
        "mean_luma": 40.779024657534244,
        "max_rgb": 61.0
      }
    ],
    "harsh": [
      {
        "plane": 0,
        "kind": "front_main",
        "pixels": 6513,
        "mean_luma": 223.6641036388761,
        "max_rgb": 255.0
      },
      {
        "plane": 1,
        "kind": "front_main",
        "pixels": 12659,
        "mean_luma": 125.34130653290148,
        "max_rgb": 201.0
      },
      {
        "plane": 2,
        "kind": "front_main",
        "pixels": 2481,
        "mean_luma": 172.05260902861747,
        "max_rgb": 231.0
      },
      {
        "plane": 3,
        "kind": "front_shaded",
        "pixels": 9908,
        "mean_luma": 121.70270603552686,
        "max_rgb": 198.0
      },
      {
        "plane": 4,
        "kind": "front_shaded",
        "pixels": 11957,
        "mean_luma": 74.22687593878064,
        "max_rgb": 159.0
      },
      {
        "plane": 5,
        "kind": "front_shaded",
        "pixels": 2555,
        "mean_luma": 36.933294481409,
        "max_rgb": 57.0
      }
    ]
  },
  "neighbor_rows": {
    "stage": [
      {
        "a": 0,
        "b": 1,
        "same_side": true,
        "display_level_difference": 81.72559864046784,
        "angle_degrees": 23.29141690797875
      },
      {
        "a": 0,
        "b": 3,
        "same_side": false,
        "display_level_difference": 85.04728288373721,
        "angle_degrees": 58.2193221094904
      },
      {
        "a": 1,
        "b": 2,
        "same_side": true,
        "display_level_difference": 49.38089190162481,
        "angle_degrees": 17.92790069639247
      },
      {
        "a": 1,
        "b": 4,
        "same_side": false,
        "display_level_difference": 52.489128088432935,
        "angle_degrees": 50.58334109298593
      },
      {
        "a": 2,
        "b": 5,
        "same_side": false,
        "display_level_difference": 138.9721351167503,
        "angle_degrees": 23.013805248938244
      },
      {
        "a": 3,
        "b": 4,
        "same_side": true,
        "display_level_difference": 49.16744384516356,
        "angle_degrees": 23.23157944193579
      },
      {
        "a": 4,
        "b": 5,
        "same_side": true,
        "display_level_difference": 37.102115126692574,
        "angle_degrees": 15.91045685211862
      }
    ],
    "harsh": [
      {
        "a": 0,
        "b": 1,
        "same_side": true,
        "display_level_difference": 98.32279710597462,
        "angle_degrees": 23.29141690797875
      },
      {
        "a": 0,
        "b": 3,
        "same_side": false,
        "display_level_difference": 101.96139760334924,
        "angle_degrees": 58.2193221094904
      },
      {
        "a": 1,
        "b": 2,
        "same_side": true,
        "display_level_difference": 46.711302495715984,
        "angle_degrees": 17.92790069639247
      },
      {
        "a": 1,
        "b": 4,
        "same_side": false,
        "display_level_difference": 51.11443059412085,
        "angle_degrees": 50.58334109298593
      },
      {
        "a": 2,
        "b": 5,
        "same_side": false,
        "display_level_difference": 135.11931454720846,
        "angle_degrees": 23.013805248938244
      },
      {
        "a": 3,
        "b": 4,
        "same_side": true,
        "display_level_difference": 47.47583009674622,
        "angle_degrees": 23.23157944193579
      },
      {
        "a": 4,
        "b": 5,
        "same_side": true,
        "display_level_difference": 37.29358145737164,
        "angle_degrees": 15.91045685211862
      }
    ]
  },
  "smoothness": {
    "stage": {
      "facet_mean": 11.17242202043571,
      "edge_excess_mean": 36.73948841810227,
      "passes": false,
      "silver_brightest_facet_mean": 246.00326538085938,
      "candidate_brightest_mean": 212.0958665131276,
      "candidate_darkest_mean": 40.779024657534244
    },
    "harsh": {
      "facet_mean": 11.062750422232634,
      "edge_excess_mean": 39.126270403861994,
      "passes": false,
      "silver_brightest_facet_mean": 235.38009643554688,
      "candidate_brightest_mean": 223.6641036388761,
      "candidate_darkest_mean": 36.933294481409
    }
  },
  "thresholds": {
    "stage_facet": 0.92,
    "stage_edge_excess": 61.5,
    "harsh_facet": 1.0,
    "harsh_edge_excess": 64.6
  },
  "planes": 6,
  "criterion_5_pass": true,
  "criterion_6_pass": false,
  "criterion_7_pass": true,
  "finish": "Reference-derived forged texture; historical smoothness limits are diagnostic only."
}
```

### proof/smoothness_pose00.txt

```text
=== pose 0.0: per-facet rough (cubic residual RMS, luma levels)
                              g0     g1     g5    g12     g7    g10   mean  mottle  grain
iron_stage                 12.83  13.56  11.74  12.76   3.71  12.42  11.17  10.32   7.85
iron_harsh                 12.95  13.37  11.31  12.87   4.32  11.56  11.06  10.22   7.79
                            edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain
iron_stage                   6.12 / 12.80        36.7 /  167.3         6.46 /  7.61       1.46            1.23
iron_harsh                   6.55 / 13.07        39.1 /  169.7         6.29 /  8.15       1.58            1.27

```

### proof/smoothness_pose20.txt

```text
=== pose 20.0: per-facet rough (cubic residual RMS, luma levels)
                              g3     g0     g1     g5    g12    g11     g7    g10   mean  mottle  grain
iron_stage                  2.28   2.64  11.69   4.71  12.96   0.96   2.43   7.10   5.60   6.23   3.74
iron_harsh                  2.34   2.52  11.39   4.50  12.82   1.16   2.39   7.08   5.53   6.11   3.69
                            edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain
iron_stage                   4.46 /  9.57        58.5 /  206.8         4.98 /  8.30       1.36            0.98
iron_harsh                   4.40 /  9.14        58.1 /  205.9         4.99 /  8.70       1.35            1.16

```

### proof/smoothness_pose45.txt

```text
=== pose 45.0: per-facet rough (cubic residual RMS, luma levels)
                              g3     g0     g1     g5    g12    g11     g7    g10     g9   mean  mottle  grain
iron_harsh                  2.14   0.94  11.40   1.63  11.46   0.25   0.86   3.12   0.29   3.57   3.48   2.35
                            edge jag mean/max   edge excess mean/max   ring grain/mottle   inset-L grain   inset-R grain
iron_harsh                   2.34 /  9.95        27.5 /  135.1         3.65 /   nan       0.70            0.92

```

### logs/final_proofs.txt

```text
PASS logs/final_extra_renders.txt
PASS logs/render_iron_harsh_45.log
PASS logs/render_iron_harsh_0_no_denoise.log
PASS logs/render_iron_harsh_0_realtime.log
PASS proof/proof_analysis.txt
PASS proof/smoothness_no_denoise.txt
PASS proof/smoothness_realtime.txt
Finished proof renders, smoothness crops, sheets and render comparisons.

```

## Scope and installation

Exactly one app file changed during authorized installation: TestBadge3DModel.dataset/silver_badge_mobile.usdz. It was already dirty from the earlier owner-authorized Iron preview; its SHA now matches corrected Iron. Full status still lists only that asset. The corrected model remains installed as explicitly requested. Renderer, Contents.json, source, helpers, config, HEAD and branches are unchanged; no commit or publication occurred. Protected originals and existing archives are preserved.

```json
{
  "revision": "floor_contact",
  "iteration": 1,
  "usdz_sha256": "85195461750aab9acf7aed470490452a07533d6c99ad73336f85b49e00cd32b0",
  "local_export_checks": "PASS",
  "usd_attribute_differences_from_previous": 0,
  "shell_exactly_matches_silver": true,
  "geometry_and_material_constants_unchanged": true,
  "plane_max_normal_difference": 0,
  "triangles": 38428,
  "bytes": 4132206,
  "changed_texture_files": 5,
  "outside_contact_band_exact_pixels": true,
  "blender_plane_tone_checks_pass": true,
  "historical_smoothness_pass": false,
  "app_test_status": "PASS: actual loaded 3D app, numeric checks and targeted contact visual review.",
  "app_installed_asset_sha256": "85195461750aab9acf7aed470490452a07533d6c99ad73336f85b49e00cd32b0",
  "app_repo_changed_this_task": true,
  "repo_status": " M ScreenTime/SupportingFiles/Assets.xcassets/TestBadge3DModel.dataset/silver_badge_mobile.usdz\n",
  "protected_original_files_verified": 105,
  "visual_limitation": "Broad crystal reflection shape remains intentionally unchanged; this correction smooths the bottom rim/contact band.",
  "blender_contact_review": "PASS",
  "app": {
    "loaded_3d": true,
    "rim_top": 145.1,
    "emblem_clip": 117,
    "emblem_mean": 84.9,
    "candidate_sha256": "85195461750aab9acf7aed470490452a07533d6c99ad73336f85b49e00cd32b0",
    "passes_numeric_app_checks": true
  },
  "app_changed_files": [
    "ScreenTime/SupportingFiles/Assets.xcassets/TestBadge3DModel.dataset/silver_badge_mobile.usdz"
  ],
  "app_contact_visual_review": "PASS, clean transition and thin dark separator retained",
  "rule_exception": "User answered yes to replacing the project asset and leaving corrected Iron installed. Explicit exception to badge AGENTS section 7.3 restoration/dirty-file stop.",
  "build_proof": [
    "ScreenTime: ** BUILD SUCCEEDED **",
    "ScreenTime-UIOnly: ** BUILD SUCCEEDED **"
  ],
  "simulator_build_proof": "ScreenTime-UIOnly (simulator): ** BUILD SUCCEEDED **",
  "tests": "skipped: presentation lane, no logic changed"
}
```

## Authorized app installation

The owner explicitly answered yes to replacing the project's badge asset and leaving corrected Iron installed for local preview. This is an owner-directed exception to badge AGENTS.md sections 1, 7.3 and 8 requiring temporary replacement, clean asset status and restoration. Scope is the single TestBadge3DModel.dataset/silver_badge_mobile.usdz asset; no renderer/source/config/helper edits, commits, branch changes or publication are authorized. The previous installed centered Iron is backed up in reports/app_floor_contact_install01/pre_task_centered_iron.usdz. Installation and actual app verification are complete. The corrected asset remains installed, as explicitly requested.

## Actual app proof

[Actual app screenshot](proof/app_iron_rest.png), [silver comparison](proof/app_silver_vs_iron_rest.png), [floor contact: silver / previous / corrected](proof/app_floor_contact_silver_before_after.png). Same-scale crops use unchanged native screenshot pixels. Latest screenshots are also in Downloads as iron_badge_in_app.png, iron_badge_floor_contact_app_comparison.png and iron_badge_app_before_after.png. Simulator project ScreenTime.xcodeproj, scheme ScreenTime-UIOnly, iPhone 17 (69A29DD2-C91E-487A-81B9-3B146DF8F07B), bundle com.antonioperedo.screentime.uidev. No physical-device or distribution test.

ScreenTime: ** BUILD SUCCEEDED **  
ScreenTime-UIOnly: ** BUILD SUCCEEDED **  
ScreenTime-UIOnly (simulator): ** BUILD SUCCEEDED **  
tests skipped: presentation lane, no logic changed

```text
/Users/antonioperedo/Desktop/badges/badge_realitykit_iron/reports/app_floor_contact_install01/app_rest.png: loaded_3d=True rim_top=145.1 emblem_clip=117 emblem_mean=84.9
```

```text
Presentation-lane corrected floor-contact Iron installation. Latest user yes explicitly authorizes replacing the single known modified badge asset and leaving corrected Iron installed; this overrides badge AGENTS7.3 temporary restoration/dirty-stop for this asset only.
Verified exact entire baseline status, HEAD, centered-Iron SHA and original external backup; copied candidate bytes to existing dataset filename.
Contents.json and renderer/source files unchanged. No other repo delta.
Ran tools/sim/gate --presentation sequentially: ScreenTime then ScreenTime-UIOnly, both succeeded. Tests skipped: presentation lane, no logic changed.
Ran tools/sim/app build for UIOnly simulator, then launch. Waited15s; terminate/wait1s/launch/wait15s twice to warm shader cache.
Captured actual app via plain tools/sim/shot, then measured with app_reference/measure_app_shot.py. loaded3DTrue,clip117<=796,rim145.1 within130..175.
Compared live whole coin/contact to Silver and pretask centered-Iron screenshots. Bottom band/reflection texture smoother, thin dark separator retained, broad crystal reflection remains. Parent visual review PASS. No new halo/geometry shift observed.
Exact tested corrected asset remains installed as the sole modified repo file. Previous centered Iron and older backups preserved. No commits/branch changes/publication/other source or helper edits. Downloads copy handled by parent.
```

## Reflection fix (Claude, 2026-10-07)

The previous contact fix smoothed only the lowest 5% of the rim, but the floor reflection mirrors a much taller strip of the rim, so crisp forged texture still sat at the top of the reflection right under the coin and the coin looked overlapped. The casing color, roughness and normal maps (USDZ_Casing_base_color, _roughness, _normal, _outer_base_color, _outer_roughness) now blend to the even contact finish by height above the floor (Y = -2.895): fully even below 1.1 units (about the lowest 19% of the coin), smoothstep back to the untouched forged texture by 2.6 units (about 44%). Nothing else changed: same usdc, geometry, names, emblem, inset and back textures; the even value is the one Codex already used at the contact. Tested in the app on the iPhone 17 simulator: the coin's lower rim and the reflection's top arc now read as smooth as silver's; loaded_3d True, emblem_clip 117, rim_top 145. Scripts and test shots: reflection_fix/ (extract_geometry.py, fade_textures.py with arguments 1.1 2.6, pack.sh, contact_center_zoom_c.png, whole_silver_codex_fixc.png). Previous version: previous/codex_contact_fix/. Gotcha: the casing has two UV sets; textures read USDZ_UV, not Machining_UV.
