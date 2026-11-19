"""Render the complete open badge with fixed studio lighting and a rotated model."""
import bpy,math,json,os
from pathlib import Path
job=json.loads(Path(os.environ['BADGE_RENDER_JOB']).read_text());sc=bpy.context.scene
sc.render.engine='CYCLES';sc.cycles.samples=job.get('samples',256);sc.cycles.use_denoising=True;sc.cycles.adaptive_threshold=.01
root=Path(job['output']);root.parent.mkdir(parents=True,exist_ok=True)
# The camera stays fixed; only badge objects turn, as in the preview.
objects=[o for o in sc.objects if o.type=='MESH' and not o.hide_render]
original={o.name:o.matrix_world.copy() for o in objects}
from mathutils import Matrix
rotation=Matrix.Rotation(math.radians(job['yaw']),4,'Z')
try:
 for ob in objects:ob.matrix_world=rotation@original[ob.name]
 sc.render.filepath=str(root);bpy.ops.render.render(write_still=True)
finally:
 for ob in objects:ob.matrix_world=original[ob.name]
 bpy.context.view_layer.update()
print('Rendered actual complete badge',job)
