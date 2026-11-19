from pathlib import Path
import importlib.util
from PIL import Image,ImageDraw,ImageOps
D=Path(__file__).resolve().parent;W=D.parent;C=W/'V_lookdev_refinement';spec=importlib.util.spec_from_file_location('controls',D/'make_controls.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.sheet([(W/'grain_hierarchy/reference_rectified.png','Owner reference'),(m.rect(D/'renders/baseline.png'),'Before: prior review light'),(m.rect(C/'close.png'),'Current: light and fine material refinement')],'owner_comparison.jpg')
m.sheet([(W.parent.parents[1]/'reference.png','Owner reference'),(W/'U_scan_fibers/cinema_full.png','Preserved baseline'),(C/'full.png','Current: same chest geometry')],'owner_full_chest.jpg',(600,600))
m.sheet([(C/'plank.png','Whole test plank'),(C/'right.png','Right side, including the lock shadow')],'owner_plank_and_right.jpg',(1000,600))
if (C/'texture_filter.png').exists():
 Image.open(C/'texture_filter.png').convert('RGB').crop((380,230,1130,740)).save(D/'texture_filter_native.jpg',quality=99)
 m.sheet([(D/'final_native.jpg','Normal texture: Linear'),(D/'texture_filter_native.jpg','Only normal texture: Closest')],'texture_filter_control.jpg',(750,510))
