# Platinum knot

Created a continuous closed beveled ribbon following the supplied reference, with three alternating over-and-under crossings. Selected candidate 02 after measuring candidate 01 inside Home and correcting its smooth platinum color and emission maps.

![Reference and actual Home render](platinum/proof/reference_vs_app.png)

The actual 3D model was built and viewed using ScreenTime-UIOnly on the iPhone 17 Simulator. ScreenTime-UIOnly: ** BUILD SUCCEEDED **. The temporary Silver slot provided the preview because Platinum currently has no 3D data set. No app code was changed. The original Silver model and all 641 tracked app files were restored byte for byte; existing branch, commit and working-tree state were preserved.

The final USDZ has 43,008 triangles, is 3.63 MB, and carries two 1024-pixel maps. Independent ARKit compliance, closed topology, face-varying normals and BadgeUV, package texture hashes, fresh import and packed editable-master checks passed. Width is 5.705 units, highest Y is 2.902, lowest Y is -2.455, and the floor gap is 0.440. Its width follows the reference's near-square proportions while fitting the height limit. There are no lights, cameras, floor, reflection objects, transforms or reserved coin names.

Highlight placement is partly fixed in the color and emission maps; actual metal shading responds during rotation. The reference's thin bright inner borders were retained. The app's existing contact line remains below this floating shape. Fine edge softness and the hole contours differ slightly from the reference.

The model and editable master remain under `platinum/mobile/` and `platinum/master/` in this workspace. Only a preview PNG goes into Downloads. The two earlier delivery folders were moved intact into `../downloads_archive/`, with their preview PNGs left in Downloads.
