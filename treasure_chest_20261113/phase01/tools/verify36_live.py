import bpy,pathlib,json,time
R=pathlib.Path('/Users/antonioperedo/Desktop/badges/treasure_chest_20261113');path=R/'phase01/candidate36/chest.blend'
assert bpy.data.filepath==str(path) and not bpy.data.is_dirty,'Unexpected file or unsaved changes'
policy=json.loads((R/'work_mode.json').read_text());assert policy['mode']=='manual' and policy['manual_work_authorized']
pref_before=bpy.context.preferences.filepaths.use_scripts_auto_execute
bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
sc=bpy.context.scene;sc.frame_set(90);bpy.context.view_layer.update()
rows=[]
for owner in list(bpy.data.objects)+list(bpy.data.shape_keys):
 if owner.animation_data:
  for fc in owner.animation_data.drivers:rows.append({'owner':owner.name,'path':fc.data_path,'simple':fc.driver.is_simple_expression,'valid':fc.driver.is_valid})
spring=float(sc.objects['Chest Rig SpringLift']['lift']);shift=float(sc.objects['Chest Rig BoltShift']['shift'])
sc.frame_set(0);bpy.context.view_layer.update()
report={'loaded_with_use_scripts':False,'global_autoexec_preference_unchanged':pref_before==bpy.context.preferences.filepaths.use_scripts_auto_execute,'autoexec_fail':bpy.app.autoexec_fail,'message':bpy.app.autoexec_fail_message,'drivers':rows,'release_spring_lift':spring,'release_pin_shift':shift,'restored_frame':sc.frame_current}
(R/'phase01/candidate36/no_autoexec_load_proof.json').write_text(json.dumps(report,indent=2)+'\n')
assert not report['autoexec_fail'],report
assert report['global_autoexec_preference_unchanged']
assert len(rows)==14,('Unexpected driver count',len(rows))
assert all(r['simple'] and r['valid'] for r in rows)
assert abs(spring-.001502)<1e-7 and abs(shift+.12)<1e-6
print(json.dumps(report))

P=R/"phase01"
exec(compile((P/"tools/pose36_screen_live.py").read_text(),"evaluated_pose36.py","exec"))
exec(compile((P/"tools/pose36_gate.py").read_text(),"pose36_gate.py","exec"))
check_pose_report36(json.loads((R/"phase01/candidate36/pose_motion_screen.json").read_text()))
exec(compile((P/"tools/rig36_negative_controls_live.py").read_text(),"actual_failure_controls36.py","exec"))
