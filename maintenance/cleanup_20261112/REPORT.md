# Badge folder storage cleanup

The owner authorized deleting unneeded material in the badges folder, then
pausing badge work. The generic make space skill normally delegates cleanup
to a Mac wide script. The owner's explicit folder scope took precedence:
that broader script was not run. Nothing outside this workspace was cleaned.

The cleanup recovered approximately 5.86 GB. Available disk space rose from
3.79 GB to 9.65 GB during the measured run.

* 1,174 identical files were replaced with verified APFS copy on write clones,
  sharing about 5.39 GB of duplicate data. Every path and exact file content
  remained. Clones have separate inodes and future writes remain independent;
  this behavior was tested before touching any badge asset. No hard links
  were created.
* 46 automatic Blender prior saves were deleted, about 461 MB. Each had an
  intact, newer working Blender file, which was retained and hash checked.
* 165 Python bytecode cache files were deleted where the Python source remained.
* Two recent duplicate groups were left alone. No cleanup operations failed.

References, current Blender sources, candidate versions, models, textures,
review evidence, Git history, production code and simulator installations
were retained. No badge geometry, material, image or rendering behavior was
changed by the cleanup. No badge build was resumed.

The manifest is report.json. Its deleted list records exactly what was
removed and the retained Blender scene for every removed automatic backup.
The cloned list records original hashes and retained anchors. inventory.json
records the initial duplicate analysis. verification.json records a separate
final content and pause check.

The new four badge run is saved as paused in its progress file and PAUSED.md.
The older royal run was already paused and remains paused. Work may continue
only after an explicit owner request. The badges are not finished.
