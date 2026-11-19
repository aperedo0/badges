# Astral sapphire material

The preview uses the new material name `CrestGem_SapphireAstral`. It selects optical profile 4 and the existing ray tracing path. Its absorption is `(10, 6, 1.6)`, giving the reference its darker blue body while retaining real surface reflections and changing internal light paths. Its index of refraction is the Sapphire range `1.76, 1.77, 1.79`. Exposure remains `0.28` and studio lighting is unchanged.

Existing Ice, Sapphire, Ruby, Amethyst and Diamond values are preserved. Only the new material name selects this finish. The change is installed only in the separate Badge Studio preview. Production has not been edited.

`runtime_material.patch` records the material lookup and the new intrinsic absorption profile. A USDZ cannot carry this runtime shader code. Any later production integration needs that material handling as well as the model. The file contains a plain deep blue UsdPreviewSurface fallback without photographs or emission textures on the stones.

There are nine visible stones on each face. Front and reverse stones are independent closed convex cuts, eighteen meshes in total. The five round mounts on each face use the approved brilliant facet geometry copied into new local stones, with separate crown and pavilion planes. The four diamond mounts on each face use actual pavilion cuts. Their culets remain separated inside the mounts. The approved Diamond asset and shader are untouched.
