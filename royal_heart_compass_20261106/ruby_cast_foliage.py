"""Continuous cast gold under the measured overlapping acanthus leaves."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_closing,binary_fill_holes,label,distance_transform_edt,gaussian_filter,map_coordinates
from reference_gold_relief import relief,gold_pixels

def cast(path):
 rgb=np.asarray(Image.open(path).convert('RGB'),float)/255
 polygon=[(116,730),(100,700),(126,678),(160,689),(174,653),(196,628),(216,653),(235,626),(280,626),(288,643),(274,661),(300,673),(325,663),(347,686),(368,721),(354,740),(358,752),(374,748),(380,766),(362,782),(344,771),(333,792),(338,823),(398,847),(420,819),(413,808),(396,783),(414,770),(409,756),(431,732),(456,714),(500,711),(525,735),(539,771),(571,807),(578,842),(553,859),(531,857),(535,846),(546,827),(522,818),(496,818),(501,840),(488,850),(468,858),(447,841),(430,850),(383,864),(316,861),(277,842),(250,824),(257,845),(247,860),(226,866),(205,856),(201,840),(211,838),(215,830),(199,825),(182,816),(166,842),(151,855),(133,858),(113,844),(90,824),(85,800),(110,822),(126,824),(137,815),(132,797),(115,785),(102,759),(107,744)]
 im=Image.new('L',(rgb.shape[1],rgb.shape[0]));ImageDraw.Draw(im).polygon(polygon,fill=255);roi=np.asarray(im)>0;yy,xx=np.mgrid[:rgb.shape[0],:rgb.shape[1]]
 # The silhouette comes from the measured contour. Photograph shadows do not
 # remove physical gold or punch accidental holes into the cast surface.
 mask=roi
 box=(85,610,590,880);crop=mask[box[1]:box[3],box[0]:box[2]];p,t=relief(crop,box,step=6)
 front=len(p)//2;distance=gaussian_filter(distance_transform_edt(crop),2.5);d=map_coordinates(distance,[p[:front,1]-box[1],p[:front,0]-box[0]],order=1)
 p[:front,2]=.003+.055*(1-np.exp(-d*.005*.45/.055));p[front:,2]=-.04
 Image.fromarray(np.uint8(crop)*255).save(Path(path).parent/'candidate13/review/cast_outline.png')
 return p,t
