#!/bin/zsh
# usage: bl_shots.sh GEOM.npz OUTPREFIX "yaw,pitch;yaw,pitch;..." SHADING
P=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
T=/Users/antonioperedo/Desktop/badges/ruby_crown_claude_20261108/tools
G=$1; O=$2; VIEWS=$3; SH=${4:-MATERIAL}
sed "s#__GEOM__#$G#" $T/blender_load_crown.py > $T/../trace/_load.py
$P -I $T/blender_link.py code $T/../trace/_load.py > /dev/null || exit 1
i=0
for v in ${(s:;:)VIEWS}; do
  i=$((i+1))
  sed "s#__VIEW__#${v}, '$SH', 17#" $T/blender_view_crown.py > $T/../trace/_view.py
  $P -I $T/blender_link.py code $T/../trace/_view.py > /dev/null
  $P -I $T/blender_link.py viewport ${O}_$i.png 800 > /dev/null
done
$P -I - <<PY
from PIL import Image
import glob
ims=[Image.open('${O}_%d.png'%k) for k in range(1,$i+1)]
ims=[x.crop((x.width//6,0,x.width*5//6,x.height)) for x in ims]
W=sum(x.width for x in ims); H=max(x.height for x in ims)
o=Image.new('RGB',(W,H)); xo=0
for x in ims: o.paste(x,(xo,0)); xo+=x.width
o.save('${O}_all.png')
PY
