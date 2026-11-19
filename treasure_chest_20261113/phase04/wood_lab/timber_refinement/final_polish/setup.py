from pathlib import Path
import json,hashlib,shutil,numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;W=D.parent;A=W/'AW_depth_hierarchy';C=W/'AX_chestnut_pigment';C.mkdir(exist_ok=True)
# The complete packed master and numerical fields are in Git before experimentation.
(D/'checkpoint.json').write_text(json.dumps(dict(commit='97cce9c',baseline=str(A),sha256=hashlib.sha256((A/'master.blend').read_bytes()).hexdigest(),dependencies=['master.blend','master_height.npz','surface.npz','albedo.png','roughness.png','normal.png','normal_masks.npz'],scope='Existing test plank only'),indent=2))
a=np.asarray(Image.open(A/'albedo.png').convert('RGB'),dtype=np.float32)/255
lin=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
t=lin*np.array([.94,1.075,.87],dtype=np.float32);weights=np.array([.2126,.7152,.0722],dtype=np.float32);t*=((lin@weights)/np.maximum(t@weights,1e-8))[:,:,None]
out=np.where(t<=.0031308,12.92*t,1.055*np.maximum(t,0)**(1/2.4)-.055)
Image.fromarray(np.uint8(np.clip(out,0,1)*255+.5)).save(C/'albedo.png')
for name in ['roughness.png','normal.png','master_height.npz','surface.npz','normal_masks.npz']:shutil.copy2(A/name,C/name)
(C/'design.json').write_text(json.dumps(dict(source='AW_depth_hierarchy',change='Luminance preserving warm chestnut pigment balance only',linear_rgb_balance=[.94,1.075,.87],geometry_normals_roughness_lighting_unchanged=True),indent=2))
(C/'.gitignore').write_text('geometry.blend\nnormal_frames.npz\n')
sheet=Image.new('RGB',(1600,660),'#202020');draw=ImageDraw.Draw(sheet)
for i,(im,label) in enumerate([(Image.open(A/'albedo.png'),'Baseline intrinsic pigment'),(Image.open(C/'albedo.png'),'Luminance held, red shifted toward burnt amber')]):
 im=im.resize((800,600));sheet.paste(im,(i*800,60));draw.text((i*800+16,20),label,fill='white')
sheet.save(D/'pigment_channels.jpg',quality=95)
print('Prepared isolated pigment trial')
