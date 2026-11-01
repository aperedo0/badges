"""Create contact sheets only after native recording has completed."""
from pathlib import Path
import subprocess,io,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
for key in sys.argv[1:]:
 R=ROOT/key;C=R/(R/'candidate.txt').read_text().strip();p=C/'full_turn.mp4'
 subprocess.run(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration',str(p)],check=True,capture_output=True)
 canvas=Image.new('RGB',(1600,830),(18,19,22));draw=ImageDraw.Draw(canvas)
 for i,t in enumerate([1.2,3.0,3.5,4.0,4.7,5.7,6.7,7.7]):
  data=subprocess.check_output(['/opt/homebrew/bin/ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
  im=Image.open(io.BytesIO(data)).crop((270,100,930,820)).resize((400,400));canvas.paste(im,((i%4)*400,(i//4)*415+15));draw.text(((i%4)*400+8,(i//4)*415+3),str(t)+' seconds',fill='white')
 canvas.save(C/'motion_review.jpg',quality=95);print(C/'motion_review.jpg')
