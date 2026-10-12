# Gold: consistent pattern through the turn

The installed crown used unevenly spaced points, unequal heights and shortened rear points to preserve its front picture. This copy replaces those with eight matching sections at 45-degree spacing: equal points, round finials and continuous curved valleys. It keeps the actual circular band, existing 17.179-degree tilt and original gold finish. Front details change slightly with the owner's permission to make the entire rotation look good.

Tested on Home through a slow full turn, including front, both sides and back, with 4x outline review. No isolated white specks or broken bright edges observed. The model fits the hard app bounds, has identity transforms and passes ARKit package checks. At 59,680 triangles it exceeds the suggested 45,000 because of the continuous curved wall and repeated detailed finials; it is smaller than the installed 74,272-triangle crown, at 4.01 MB.

The updated preview is installed in the main iPhone 17 simulator. The actual app repo and all other badges remain unchanged. Temporary captures and test copies were removed as requested; no Downloads review folder was created. Rebuild with Blender's bundled Python using `tools/build.py`; it reads the preserved prior Gold model.

Validation ran sequentially on a private app copy containing only this Gold model substitution:

```text
ScreenTime: ** BUILD SUCCEEDED **
ScreenTime-UIOnly: ** BUILD SUCCEEDED **
DeviceActivityReportExtension: ** BUILD SUCCEEDED **
** TEST SUCCEEDED **
```

The test log did not emit the older `Executed N tests` summary format. The result bundle reports 1,879 passed, 0 failed, 0 skipped. A byte-content audit confirmed all 43 protected app files unchanged and the final USDZ contents identical to the tested preview.
