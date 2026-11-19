# Bottom forged iron refinement

Owner review pending. Only the existing Lab Chest Lower Rim is developed. The provisionally approved BC wood, other chest components and original complete scene are preserved. The reference remains the single shared image already set up in Blender.

## Evidence and changes

The starting material was tested unchanged under its existing lights, a neutral studio HDRI at two orientations, clean iron control shaders, and warmer environmental illumination. The clean controls used Filament's published sRGB C4C6C6, converted to scene linear RGB, with metallic 1 and independently tested roughness. They exposed useful relief that the old dark conducting base color concealed. They are diagnostic controls, not the final finish. Removing individual source lights identified the broad fill as the main cause of the continuous bright upper band. Changing the rear light had little effect.

The selected candidate separates blackened conductive iron, localized clean exposed conductor, and opaque dielectric scale. Each branch has independent color and roughness controls. Existing source roughness fields supply separate oxide and sparse wear masks. Existing damage locations influence edge wear, while an intermittent edge mask prevents universal painted outlines. No gold color, emission or directional illumination is painted into the maps.

The existing medium hammer field remains the main surface source. Local planar fitting flattens selected existing depression floors without generating new hammer cells. One Simple subdivision step resolves physical vertex displacement of that medium field. Its matching coarse bump is disabled, so the same relief is not counted twice. Fine source fibers, pitting, shallow scale and limited open reference guided forge laps remain separately adjustable normal relief. Original primary dents and edge chips remain. Contact regions are protected.

A controlled final correction darkened only the opaque oxide pigmentation from (0.030, 0.024, 0.019) to (0.012, 0.009, 0.006) in scene linear values. Conductive iron reflectance, roughness, geometry and lighting remained fixed in that comparison. This reduced the gray body appearance without suppressing reflection definition.

The selected reflection study uses a desaturated free studio HDRI, reduced warm key light and a smaller elevated warm fill. Original Test plank master lighting and approved wood shading remain unchanged. A separate Bottom iron reflection review scene saves the reflection conditions. Surrounding finishes shown in contextual PNGs are temporary render substitutions only.

## Visual evaluation

Actual Cycles renders were opened for all diagnostic groups and meaningful refinement comparisons. Comparisons include left and right bays, clean controls, gray grazing views, two displacement densities, old versus professional medium height data, and coating coverage. Final images include original lighting as well as identical reflection study lighting on the baseline and selected candidate. The sheets do not imply that all differences come from the material alone.

Useful improvements are clearer face reflection variation, separation of material layers, resolved secondary physical relief, retained small pits, localized exposed wear, restrained shallow forge laps, and a much thinner warmer upper reflection under the isolated review lighting.

Remaining differences are significant: the original reference has more irregular angular plate formations, sharper broken transitions, stronger selective bright scars and more boldly damaged bevels. Some selected formations remain rounded and some fine marks resemble scratches. The reference's warm edge is brighter than the isolated review result. The new material alone does not eliminate the old broad white reflection when illuminated by the original fill. This is the strongest retained candidate from this round, not a claim of exact reference fidelity or owner approval.

## Rejected or limited experiments

The newly inspected cgbookcase Battered Metal 02 height produced cloudy and quieter forms rather than an improvement. Its public source map is 8 bit; saving processed output at 16 bit does not add captured precision. Existing float authoring data is preserved. Low density physical displacement lost definition; the denser grid was retained. Unrestricted oxide coverage looked like peeling paint; constrained coverage was more cohesive. A final lower coverage trial produced no clear overall gain. A separate geometric test flattened eight manually selected existing face regions; the actual render did not close the angular form gap enough to justify keeping it. The stronger pretest geometry was retained. Broadly brightened environments flattened the face. Lowering studio environment strength from 0.45 to 0.18 hid useful face detail and was rejected. An initial lap implementation had endpoint NaNs and discontinuous signed lip evaluation; these were corrected and finite data asserted before selection.

Do not repeat strength sweeps or add random detail. Further form improvement calls for deliberate local sculpting of selected existing formations, with owner direction, rather than another global noise generator. The owner alone judges acceptance and transfer. Brass and all other iron remain outside scope.

## Recovery and resources

Initial complete Git checkpoint: 546d617. baseline.blend and checkpoint_validation.json prove restoration of the starting wood and iron with required packed images. The selected complete master and final validation records are beside the selected candidate. Editable float fields, physical before and after arrays, maps, scripts and provenance are retained. No paid resource, new installation, app change or AI reviewer was used.

Published clean iron control: https://google.github.io/filament/main/materials.html

Studio Small 03, Greg Zaal, CC0: https://polyhaven.com/a/studio_small_03

Battered Metal 02, cgbookcase, free CC0: https://www.cgbookcase.com/textures/battered-metal-02

Actual downloads, hashes and license pages are in resources/SOURCES.json. Existing ambientCG Metal055A and Metal003 data and provenance remain in ../lower_iron/resources.

## Owner requested knob finish

After inspecting the saved iron, the owner requested the same finish on the two small knobs above the textured bottom strip. Lab Chest Rail Rivet 1 3 and Lab Chest Rail Rivet 1 4 now share the existing iron material with physical atlas scale UVs. Their geometry, positions and hierarchy are unchanged. Larger corner and center knobs, all other hardware and approved wood remain untouched. This explicit direction overrides the brass appearance of those two knobs in the reference. N_charcoal_scale preserves the complete scene before this request; P_iron_knobs is the selected saved scene. Context rendering preserves these two actual material assignments while temporarily coloring other hardware.

Final validation reopened the saved project in a fresh Blender process and matched the live save hash. The two knob meshes remain 289 vertices each with exact original geometry. The addon offscreen viewport capture returned a black image and was not used as visual evidence; actual saved Cycles renders were opened and inspected instead. The live API confirms the selected image is displayed in the existing review editor.
