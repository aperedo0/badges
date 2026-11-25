# Ruby Hourglass

The editable scene is `Ruby Hourglass.blend`. The app model is `mobile/ruby_hourglass.usdz`. The two rubies meet at a narrow waist, each cut on its front and back. Separate bronze rails follow their sides. The reference is packed in the Blender file.

[Reference, Blender render and iPhone capture](Ruby%20Hourglass%20Comparison.png) · [Blender render](Ruby%20Hourglass.png)

## App checks

The iPhone 17 private preview loaded the delivered USDZ byte for byte. Both ruby cores received the native ruby shader, including in the floor reflection. Nine captures cover the front, early turn, both profiles, back and intervening angles. The package contains 8,968 triangles and occupies 196,452 bytes. The upper stone has 50 distinct optical planes and the lower stone has 58. The app’s Swift extractor accepted both stones and their reflections. Each solid closes when matching vertices at flat facet boundaries. [Validation](validation.json)

The studio render has a warm strip reflection on the upper right and lower left. The phone uses its own fixed studio, which produces a darker red and places the brightest reflection on the lower stone. Each ruby has a partially transmitting polished surface over its optical core. A control captured without the cores verified internal reflections at rest and during the first turn.

The fifth candidate removed the broken red edge glint and horizontal streaks across the lower end. Fresh finish review still found a narrow highlight breaking into alternating pixels on the lower left rail near the end of the turn, when the badge was about 54 pixels tall. The back also shows several cloudy patches on the upper stone near its waist. The badge remains a review candidate. The badge fresh review workflow calls for an owner look after recurring finish issues across multiple revisions. No final likeness score was assigned.

The private preview entry is **Ruby Hourglass**. Production integration remains pending. The repository excludes Blender binaries from Git; the editable file is available locally beside this report.
