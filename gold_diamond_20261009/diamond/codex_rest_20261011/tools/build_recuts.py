"""Recut copies of the installed gem, preserving the crown and resting azimuth."""
from pathlib import Path
import hashlib
import json
import math
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent/'gem_shader_20261011/model/build_gem.py'

def build(name,pavilion,lower_extra):
    namespace={'__name__':'recut_builder','__file__':str(SOURCE)}
    exec(compile(SOURCE.read_text(),str(SOURCE),'exec'),namespace)
    bottom=namespace['CULET_Y']+namespace['GIRDLE_APOTHEM']*math.tan(math.radians(pavilion))
    translation=bottom-namespace['GIRDLE_BOTTOM_Y']
    namespace['GIRDLE_BOTTOM_Y']=bottom
    namespace['GIRDLE_TOP_Y']+=translation
    namespace['TABLE_Y']+=translation
    namespace['STAR_TIP_Y']+=translation
    namespace['LOWER_GIRDLE_EXTRA_DEGREES']=lower_extra
    directory=ROOT/'recuts'/name
    directory.mkdir(parents=True,exist_ok=True)
    planes=namespace['facet_planes']()
    vertices=namespace['intersect_planes'](planes)
    polygons=namespace['facet_polygons'](planes,vertices)
    assert all(p is not None for p in polygons)
    triangles=namespace['triangulate'](polygons)
    namespace['run_checks'](planes,vertices,polygons,triangles)
    namespace['write_usd'](directory,planes,vertices,triangles)
    np.savez(directory/'gem_planes.npz',normals=np.array([p[1] for p in planes]),offsets=np.array([p[2] for p in planes]),families=np.array([p[0] for p in planes]),ALLP=np.array([[vertices[a],vertices[b],vertices[c]] for _,a,b,c in triangles]))
    model=directory/'diamond_badge_mobile.usdz'
    facts={'pavilion_degrees':pavilion,'lower_girdle_extra_degrees':lower_extra,'rest_azimuth_degrees':22.5,'crown_translation_y':translation,'girdle_bottom_y':bottom,'girdle_top_y':namespace['GIRDLE_TOP_Y'],'table_y':namespace['TABLE_Y'],'culet_y':namespace['CULET_Y'],'planes':len(planes),'triangles':len(triangles),'vertices':len(vertices),'bounds':[vertices.min(0).tolist(),vertices.max(0).tolist()],'bytes':model.stat().st_size,'sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'crown_profile':'Original crown translated with the girdle; its angles and table radius are unchanged.'}
    (directory/'geometry.json').write_text(json.dumps(facts,indent=2))
    shader=ROOT/'diagnostics/05_energy_preserving_exit/BadgeGemSurface.metal'
    (directory/'BadgeGemSurface.metal').write_bytes(shader.read_bytes())
    (directory/'NOTES.txt').write_text(f'Pavilion {pavilion} degrees, lower girdle {pavilion+lower_extra} degrees. Crown translated down {abs(translation):.3f} units with the girdle.\nFixed width, culet and 22.5 degree azimuth; only the cut changes, alongside the diagnosed bounded exit correction.\n')
    print(json.dumps(facts,indent=2))

if __name__=='__main__':
    for args in [('01_40p5',40.5,3.0),('02_41',41.0,2.0),('03_41p5',41.5,3.0)]:build(*args)
