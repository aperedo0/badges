import bpy
from pathlib import Path
R=Path('/Users/antonioperedo/Desktop/badges/royal_heart_compass_20261106')
p=R/'amethyst_crown/candidate14/source/amethyst_crown.blend'
with bpy.data.libraries.load(str(p),link=False) as (source,target):
 target.scenes=[source.scenes[0]]
scene=target.scenes[0];bpy.context.window.scene=scene
print('Retained complete crown scene loaded from',p)
