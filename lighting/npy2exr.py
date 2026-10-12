import sys, bpy, numpy as np
src, out = sys.argv[sys.argv.index('--') + 1:][:2]
a = np.load(src); h, w, _ = a.shape
rgba = np.ones((h, w, 4), dtype=np.float32); rgba[..., :3] = a[::-1]
img = bpy.data.images.new('env', w, h, alpha=True, float_buffer=True)
img.colorspace_settings.name = 'Non-Color'
img.pixels.foreach_set(rgba.ravel())
s = bpy.context.scene.render.image_settings
s.media_type = 'IMAGE'
s.file_format, s.color_mode, s.color_depth, s.exr_codec = 'OPEN_EXR', 'RGBA', '32', 'NONE'
img.filepath_raw = out; img.file_format = 'OPEN_EXR'
img.save_render(out, scene=bpy.context.scene)
print('WROTE', out)
