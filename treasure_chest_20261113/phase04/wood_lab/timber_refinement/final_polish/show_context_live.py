import bpy,json
from pathlib import Path
D=Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113/phase04/wood_lab/timber_refinement/final_polish');C=D.parent/'BC_final_polish'
assert Path(bpy.data.filepath)==C/'master.blend'
windows=list(bpy.context.window_manager.windows);views=[(w,a) for w in windows for a in w.screen.areas if a.type=='IMAGE_EDITOR' and a.spaces.active.image and a.spaces.active.image.name=='Render Result']
# Display the completed isolated context in the existing render window only.
# The main reference editor, main 3D view and owner camera framing remain untouched.
if views:
 image=bpy.data.images.load(str(C/'context_contact_softwarm_final.png'),check_existing=True);image.name='Final wood polish context review';image.use_view_as_render=False;image.pack()
 for w,a in views:
  a.spaces.active.image=image
  region=next(r for r in a.regions if r.type=='WINDOW')
  with bpy.context.temp_override(window=w,area=a,region=region):bpy.ops.image.view_all(fit_view=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(C/'master.blend'),compress=True)
print(json.dumps(dict(file=bpy.data.filepath,review_render_shown_in_existing_window=bool(views),original_reference_editor_and_main_3D_view_untouched=True)))
