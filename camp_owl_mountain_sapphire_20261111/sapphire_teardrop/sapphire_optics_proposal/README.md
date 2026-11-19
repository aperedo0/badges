Sapphire specific optical controls proposal

Not applied. The preview and production sources remain unchanged. This adds one new material name, CrestGem_SapphireTeardrop, mapped to profile19. Only a model using that material can take this path. Initial absorption, density, light gain and exposure exactly retain profile18 behavior. The new route provides separate values to tune for this sapphire while preserving all current gems and their lighting.

The existing profile18 treatment is physically traced and keeps the broad crown, but current Blender review76 identifies dark fragmented inner reflections, grey highlights and insufficient lower cyan. Geometry only tests removed the pattern by flattening the rear, at the cost of a glassy surface and weaker facet readability. Candidate18 remains the retained faceted baseline.

Permission is requested before applying this patch because workspace AGENTS.md section5 says Never edit app code. If authorized, apply only to the separate preview and tune the new Sapphire specific values in matching Blender optical renders before final native validation. The Diamond shader, studio, all other material profiles and production app remain unchanged.
