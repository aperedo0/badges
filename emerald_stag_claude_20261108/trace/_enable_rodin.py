import bpy
for sc in bpy.data.scenes:
    sc.blendermcp_use_hyper3d = True
    sc.blendermcp_hyper3d_mode = 'MAIN_SITE'
try:
    r = bpy.ops.blendermcp.set_hyper3d_free_trial_api_key()
    print('free trial operator', r)
except Exception as e:
    print('operator failed', e)
    for sc in bpy.data.scenes:
        sc.blendermcp_hyper3d_api_key = 'vibecoding'
print('scene', bpy.context.scene.name, 'use_hyper3d', bpy.context.scene.blendermcp_use_hyper3d, 'mode', bpy.context.scene.blendermcp_hyper3d_mode)
