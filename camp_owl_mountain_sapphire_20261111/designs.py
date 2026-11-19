"""Measured smooth outlines for four separate, solid 3D badges."""
from pathlib import Path
import re, json, math
import numpy as np
from shapely.geometry import Polygon, Point, LineString, box
from shapely import affinity
from shapely.ops import unary_union, polygonize

ROOT = Path(__file__).resolve().parent

def path(s):
    tokens = re.findall(r'[MLCQZmlcqz]|[-+]?(?:\d*\.\d+|\d+)', s)
    out, current, start, i, cmd = [], np.zeros(2), None, 0, None
    while i < len(tokens):
        if tokens[i].isalpha():
            cmd = tokens[i].upper(); i += 1
        if cmd == 'Z':
            break
        count = {'M':2,'L':2,'C':6,'Q':4}[cmd]
        q = np.asarray([float(v) for v in tokens[i:i+count]]).reshape(-1,2); i += count
        if cmd in ['M','L']:
            current = q[0]; out.append(current.copy())
            if start is None: start = current.copy()
            if cmd == 'M': cmd = 'L'
        else:
            n = max(6,min(100,int(np.linalg.norm(np.diff(np.vstack([current,q]),axis=0),axis=1).sum()/3)))
            t = np.linspace(0,1,n+1)[1:,None]
            if cmd == 'C':
                a = (1-t)**3*current + 3*(1-t)**2*t*q[0]+3*(1-t)*t*t*q[1]+t**3*q[2]
            else:
                a = (1-t)**2*current+2*(1-t)*t*q[0]+t*t*q[1]
            out.extend(a); current=q[-1]
    g=Polygon(out).buffer(0)
    return g.simplify(min(.45,max(g.bounds[2]-g.bounds[0],g.bounds[3]-g.bounds[1])*.00035),preserve_topology=True)

def ellipse(x,y,rx,ry=None,n=160):
    return affinity.scale(Point(x,y).buffer(1,quad_segs=n//4),rx,rx if ry is None else ry)

def shape(g):
    if g.is_empty: return []
    gs = list(g.geoms) if hasattr(g,'geoms') else [g]
    return [dict(exterior=np.asarray(p.exterior.coords).round(4).tolist(),holes=[np.asarray(h.coords).round(4).tolist() for h in p.interiors]) for p in gs if isinstance(p,Polygon) and p.area>1]

def mirror(g,axis=626):
    return affinity.scale(g,xfact=-1,yfact=1,origin=(axis,0))

def star(x,y,rx,ry):
    d=path('M 0 -1 C .12 -.25 .18 -.16 1 0 C .22 .12 .12 .22 0 1 C -.12 .23 -.23 .12 -1 0 C -.23 -.12 -.12 -.25 0 -1 Z')
    return affinity.translate(affinity.scale(d,rx,ry,origin=(0,0)),x,y)

def stroke(points,width):
    return LineString(points).buffer(width/2,cap_style='round',join_style='round').simplify(.4)

def sampled_bezier(s):
    # Open line paths use the same smooth sampling, with a very small closing return.
    p=path(s+' Z')
    return np.asarray(p.exterior.coords)

class Design:
    def __init__(self,slug,name,axis,top,bottom):
        self.slug,self.name=slug,name
        self.units=dict(S=5.45/(bottom-top),axis=axis,top=top,width_px=1254,height_px=1254)
        self.pieces=[]
    def add(self,name,g,material='Gold',rim=0,bevel=8,height=.045,base=None,dome=0,ignore=None,**kw):
        p=dict(name=name,outline=shape(g),material=material,side='Side',top=dict(kind='flat',height=height,dome=dome))
        if bevel:p['bevel']=dict(width=bevel,height=min(.045,bevel*self.units['S']*.85))
        if rim:
            p['rim']=dict(width=rim,height=.022,material='Gold')
            p['cells']=[dict(material=material,shape=shape(g))]
            p['material']='Gold'
        if base is not None:p['base']=base
        if ignore:p['base_ignore']=ignore
        p.update(kw);self.pieces.append(p)
        return g
    def enamel(self,name,g,base=None,bevel=6,rim=3,height=.045,dome=0,**kw):
        return self.add(name,g,'Enamel',rim,bevel,height,base,dome,**kw)
    def save(self):
        folder=ROOT/self.slug;folder.mkdir(exist_ok=True)
        spec=dict(name=self.name,units=self.units,gap=.012,box=[0,0,1254,1254],pieces=self.pieces)
        (folder/'PIECES.json').write_text(json.dumps(spec,indent=1)+'\n')
        (folder/'palette_base.json').write_text(json.dumps(dict(Gold=dict(albedo=[.83,.43,.045],metallic=1,roughness=.22),Side=dict(albedo=[.30,.115,.015],metallic=1,roughness=.5),DarkMetal=dict(albedo=[.055,.025,.008],metallic=1,roughness=.32),Enamel=dict(albedo=[.03,.06,.12],metallic=1,roughness=.18),WoodInlay=dict(albedo=[.24,.055,.009],metallic=.1,roughness=.4),Pupil=dict(albedo=[.015,.006,.002],metallic=.25,roughness=.12),Sapphire=dict(albedo=[.005,.04,.65],metallic=0,roughness=.08)),indent=1)+'\n')
        (folder/'enamel_config.json').write_text(json.dumps(dict(texture_px=1024,materials=dict(Enamel=dict(roughness=.18,max_display=.93,gold_exclusion_border_px=18))),indent=1)+'\n')
        print(self.slug,len(self.pieces),'real solid pieces',flush=True)

def campfire():
    d=Design('campfire_night','Campfire Night',615,85,1165)
    circle=ellipse(615,625,518,540)
    inner=circle.buffer(-14)
    d.enamel('night_backplate',inner,base=.075,bevel=8,rim=0,height=.025)
    mountains=path('M 25 675 C 175 615 227 576 306 531 L 419 457 C 438 447 450 448 469 460 L 549 508 L 669 550 L 812 483 C 833 468 848 470 872 484 L 955 532 L 1220 676 L 1250 900 L 0 900 Z').intersection(circle.buffer(-13))
    d.enamel('purple_mountain_range',mountains)
    ground=path('M 125 824 C 357 738 881 732 1109 821 L 1125 1098 L 615 1156 L 120 1098 Z').intersection(circle.buffer(-9))
    d.enamel('green_campground',ground,no_clip=True)
    moon=path('M 629 149 C 568 132 508 174 508 238 C 507 305 559 345 617 335 C 662 329 693 297 692 264 C 667 285 631 287 606 265 C 572 237 577 188 626 158 C 639 152 637 149 629 149 Z')
    d.enamel('crescent_moon',moon,bevel=5,rim=3,height=.055)
    for name,x,y,rx,ry in [('star_left',395,296,55,65),('star_right',851,329,59,70)]:
        d.enamel(name,star(x,y,rx,ry),bevel=5,rim=3,height=.055)
    for i,(x,y,r) in enumerate([(471,196,10),(756,202,13),(779,278,9),(914,275,8),(298,336,10),(470,385,13),(357,438,8),(731,367,8),(793,440,8),(914,432,8)]):
        d.add(f'night_gold_dot_{i:02}',ellipse(x,y,r),bevel=3,height=.045,dome=.025)
    small=path('M 378 553 C 371 558 365 580 353 597 L 339 612 C 329 625 346 637 359 628 L 342 652 L 329 672 C 324 686 344 690 354 684 L 343 704 C 357 723 379 714 390 719 C 406 716 431 715 435 704 L 414 684 C 432 686 442 673 431 662 L 408 630 C 424 635 433 623 421 611 L 401 591 C 386 567 386 552 378 553 Z')
    d.enamel('small_pine_left',small)
    d.enamel('small_pine_right',mirror(small,630))
    trunk=path('M 210 710 L 266 710 L 273 806 L 201 823 Z')
    canopy0=path('M 258 399 C 269 394 277 414 280 434 C 290 474 302 497 318 523 C 331 541 312 553 292 542 C 279 555 265 551 255 543 C 243 555 227 550 219 539 C 198 547 180 540 168 530 C 171 516 190 504 211 477 C 235 446 242 408 258 399 Z')
    canopy1=path('M 249 499 C 264 489 274 508 280 530 C 293 568 312 593 337 622 C 349 640 330 654 306 646 C 289 665 267 661 250 651 C 230 672 202 659 193 648 C 164 660 143 652 125 639 C 117 630 126 620 139 609 C 183 578 223 531 249 499 Z')
    canopy2=path('M 245 600 C 259 590 276 617 283 637 C 300 675 328 706 355 726 C 373 745 346 758 326 746 C 312 764 293 760 280 749 C 261 768 240 764 225 753 C 205 770 183 759 173 749 C 153 761 138 750 129 741 C 113 751 107 736 119 723 C 151 701 196 654 221 620 C 230 608 236 603 245 600 Z')
    for side,dx,dy in [('left',0,0),('right',0,16)]:
        trans=lambda p: affinity.translate(p if side=='left' else mirror(p,630),dx,dy)
        d.enamel('pine_'+side+'_trunk',trans(trunk))
        d.enamel('pine_'+side+'_lower',trans(canopy2).intersection(inner))
        d.enamel('pine_'+side+'_middle',trans(canopy1).intersection(circle.buffer(-9)))
        d.enamel('pine_'+side+'_top',trans(canopy0))
    left_log=path('M 341 871 C 397 849 470 836 569 810 L 642 868 L 420 995 C 378 1009 337 976 323 935 C 310 906 318 881 341 871 Z')
    right_log=path('M 688 809 C 763 829 835 846 886 881 C 920 906 910 946 886 978 C 866 1001 843 1003 816 988 L 607 884 Z')
    d.enamel('left_crossed_log',left_log,bevel=8,rim=4,height=.055)
    d.enamel('right_crossed_log',right_log,bevel=8,rim=4,height=.055)
    for name,x,y,rx,ry,angle in [('left',398,951,55,64,-27),('right',846,953,54,62,27)]:
        d.enamel('log_end_'+name,affinity.rotate(ellipse(x,y,rx,ry),angle),bevel=5,rim=3,height=.045,dome=.008)
        t=np.linspace(0,3.6*np.pi,140);rr=np.linspace(2,34,len(t));coords=np.c_[x+rr*np.cos(t),y+.96*rr*np.sin(t)]
        d.add('wood_spiral_'+name,stroke(coords,5.5),'WoodInlay',bevel=1,height=.015)
    front_log=path('M 603 828 C 614 822 647 826 660 842 L 707 991 C 718 1042 680 1074 630 1074 C 579 1073 539 1044 549 995 Z')
    d.enamel('upright_front_log',front_log,bevel=7,rim=4,height=.05)
    d.enamel('front_log_end',ellipse(629,1016,70,63),bevel=5,rim=3,height=.04)
    t=np.linspace(0,3.6*np.pi,150);rr=np.linspace(2,43,len(t));d.add('wood_spiral_front',stroke(np.c_[629+rr*np.cos(t),1016+.83*rr*np.sin(t)],6),'WoodInlay',bevel=1,height=.015)
    flame_outer=path('M 444 863 C 391 851 365 807 376 750 C 378 718 389 686 402 670 C 416 676 419 705 443 708 C 414 626 446 570 495 530 C 526 501 544 486 546 461 C 550 438 576 459 585 497 C 611 463 615 416 598 380 C 585 351 614 357 640 372 C 713 410 751 472 749 548 C 743 580 731 608 743 636 C 756 641 775 619 783 595 C 811 614 833 657 838 697 C 866 781 827 847 751 865 C 660 894 524 897 444 863 Z')
    flame_middle=path('M 497 863 C 469 846 448 814 453 775 C 471 788 478 799 492 802 C 469 733 477 662 523 619 C 576 575 623 564 650 518 C 664 487 678 494 685 528 C 700 566 691 621 709 651 C 725 684 762 685 775 726 C 801 795 752 852 699 874 C 633 891 560 889 497 863 Z')
    flame_inner=path('M 579 869 C 537 848 519 815 529 770 C 532 749 542 729 550 720 C 556 738 566 763 582 767 C 571 717 592 668 627 640 C 640 629 647 627 650 630 C 636 680 650 711 682 744 C 720 780 723 819 689 857 L 675 868 C 663 851 648 844 630 845 C 606 844 592 854 579 869 Z')
    for name,g in [('outer_red_flame',flame_outer),('middle_amber_flame',flame_middle),('inner_yellow_flame',flame_inner)]:
        d.enamel(name,g,bevel=6,rim=3,height=.052,dome=.008)
    rocks=[('back_left','M 294 906 C 268 906 253 939 258 968 C 258 991 274 1007 293 1013 L 334 979 C 334 943 316 911 294 906 Z'),('back_right',None),('middle_left','M 336 976 C 300 978 286 1003 301 1033 L 350 1070 C 378 1078 408 1052 410 1030 C 395 995 369 978 336 976 Z'),('middle_right',None),('front_left','M 464 1000 C 416 1004 389 1048 391 1082 C 414 1118 473 1137 532 1132 C 555 1107 566 1086 554 1060 C 534 1021 502 1000 464 1000 Z'),('front_right',None),('front_center','M 630 1044 C 589 1042 544 1070 538 1114 C 534 1135 542 1147 562 1149 C 610 1158 667 1154 707 1143 C 711 1113 697 1078 669 1057 C 658 1049 646 1045 630 1044 Z')]
    pending={}
    for name,s in rocks:
        if s:g=path(s);pending[name]=g
        else:g=mirror(pending[name.replace('right','left')],630)
        d.enamel('stone_'+name,g.intersection(circle.buffer(-15)),bevel=6,rim=3,height=.05,dome=.025)
    for i,(x,y,ang) in enumerate([(259,862,-38),(279,849,-6),(298,855,31),(891,832,-20),(912,837,25),(955,877,-20),(979,880,22)]):
        g=path('M 0 0 C -12 -14 -12 -31 -4 -35 C 5 -35 6 -16 0 0 Z');g=affinity.translate(affinity.rotate(g,ang,origin=(0,0)),x,y)
        d.add('grass_blade_'+str(i),g,bevel=2,height=.025)
    d.add('outer_gold_setting',circle.difference(circle.buffer(-20)),bevel=6,height=.055)
    d.save()

def owl():
    d=Design('amber_owl','Amber Owl',626,22,1187)
    circle=ellipse(626,604.5,586,582.5);inner=circle.buffer(-18)
    d.enamel('blue_enamel_backplate',inner,base=.075,bevel=8,rim=0,height=.025)
    arc=np.c_[626+426*np.cos(np.linspace(np.pi*1.18,np.pi*1.82,160)),636+426*np.sin(np.linspace(np.pi*1.18,np.pi*1.82,160))]
    d.add('upper_star_arc',stroke(arc,8),bevel=3,height=.045)
    d.enamel('head_amber_disc',ellipse(626,727,388,388).intersection(inner),bevel=7,rim=4,height=.05)
    wing=path('M 358 735 C 272 736 195 792 179 873 C 164 962 198 1042 271 1091 L 421 1160 C 388 1073 388 984 414 915 C 423 833 414 765 358 735 Z')
    d.enamel('left_amber_wing',wing.intersection(inner))
    d.enamel('right_amber_wing',mirror(wing).intersection(inner))
    outerfeather=path('M 435 762 C 363 783 346 839 371 914 C 392 970 415 1011 448 1032 C 421 930 455 852 486 812 Z')
    innerfeather=path('M 510 771 C 440 812 427 888 457 980 C 475 1041 509 1102 556 1142 C 528 1045 549 965 579 878 Z')
    centerfeather=path('M 626 785 C 574 779 519 828 515 894 C 505 980 545 1057 626 1162 C 701 1060 746 982 737 895 C 731 824 679 780 626 785 Z')
    for n,g in [('outer_left_feather',outerfeather),('outer_right_feather',mirror(outerfeather)),('inner_left_feather',innerfeather),('inner_right_feather',mirror(innerfeather)),('central_cream_breast',centerfeather)]:
        d.enamel(n,g.intersection(inner),bevel=6,rim=3,height=.045)
    face=path('M 293 598 C 310 554 354 529 406 532 C 487 537 568 595 626 677 L 626 843 C 575 796 537 782 462 774 C 363 760 316 723 301 673 C 292 645 287 619 293 598 Z')
    d.enamel('cream_face_mask',unary_union([face,mirror(face)]),bevel=6,rim=3,height=.05)
    for side,x in [('left',488),('right',764)]:
        d.enamel(side+'_amber_iris',ellipse(x,603,78,67),bevel=5,rim=3,height=.045,dome=.012)
        d.add(side+'_dark_pupil',ellipse(x-3 if side=='left' else x+3,585,36,44),'Pupil',bevel=6,height=.035,dome=.025)
    horn=path('M 251 238 C 249 300 277 344 353 375 C 489 427 586 483 626 642 L 591 691 C 563 624 526 580 450 542 C 364 501 306 512 258 473 C 215 438 209 353 251 238 Z')
    upper=path('M 251 238 C 256 302 309 329 393 357 C 537 402 596 479 626 642 C 577 521 505 482 406 448 C 328 422 263 401 242 355 C 230 323 236 280 251 238 Z')
    for name,g,u in [('left_cream_brow_blade',horn,upper),('right_cream_brow_blade',mirror(horn),mirror(upper))]:
        d.enamel(name,g,bevel=7,rim=4,height=.055,cells=[dict(material='Enamel',shape=shape(g.difference(u))),dict(material='Enamel',shape=shape(g.intersection(u)))],lines=dict(width=7,height=.02,material='Gold'))
    beak=path('M 626 650 C 604 682 593 719 606 753 L 626 804 L 646 753 C 659 719 649 682 626 650 Z')
    d.enamel('central_gold_beak',beak,bevel=5,rim=3,height=.055)
    d.enamel('top_four_point_star',star(626,202,126,129),bevel=6,rim=3,height=.05)
    d.add('outer_gold_setting',circle.difference(circle.buffer(-25)),bevel=8,height=.065)
    d.save()

def partition(g,lines):
    net=unary_union([g.boundary]+[LineString(p).intersection(g) for p in lines])
    return [dict(material='Enamel',shape=shape(p)) for p in polygonize(net) if p.area>3 and g.buffer(.1).contains(p.representative_point())]

def mountain():
    d=Design('radiant_mountain','Radiant Mountain',628,70,1198)
    outline=path('M 628 70 C 923 67 1149 307 1151 598 C 1154 817 1006 1018 815 1112 L 628 1198 L 432 1105 C 235 1045 93 842 95 608 C 91 310 319 70 628 70 Z')
    inner=outline.buffer(-18)
    sky=inner
    skycuts=[[(477,105),(537,260),(568,350)],[(627,91),(627,255)],[(775,111),(719,259),(687,351)],[(332,222),(493,323)],[(925,222),(762,323)],[(186,393),(480,404)],[(1068,393),(772,404)],[(183,498),(238,624)],[(221,500),(247,581)],[(1031,500),(1008,583)],[(1070,498),(1017,624)]]
    d.add('blue_glass_sky',sky,'Enamel',bevel=8,height=.03,base=.07,cells=[dict(material='Enamel',shape=shape(sky))],ridge_paths=skycuts,lines=dict(width=8,height=.025,material='Gold'))
    def pane(name,g,lines=None,base=None):
        kw={}
        if lines:kw=dict(cells=[dict(material='Enamel',shape=shape(g))],ridge_paths=lines,lines=dict(width=7,height=.023,material='Gold'))
        d.enamel(name,g,bevel=6,rim=3,height=.042,base=base,**kw)
        d.pieces[-1]['rim'].update(outer_material='DarkMetal',outer_width=2.2)
    rays=[Polygon([(626,110),(606,252),(646,252)]),Polygon([(343,255),(492,302),(473,353)]),Polygon([(908,255),(761,302),(780,353)]),Polygon([(242,409),(475,402),(478,456)]),Polygon([(1011,409),(778,402),(775,456)])]
    for i,g in enumerate(rays):
        coords=np.asarray(g.exterior.coords)[:-1];center=np.array([627.,402.]);indices=np.argsort(np.linalg.norm(coords-center,axis=1))[:2];base=coords[indices];extended=base+(center-base)/np.linalg.norm(center-base,axis=1,keepdims=True)*30
        g=unary_union([g,Polygon(np.vstack([base,extended[::-1]]))])
        pane('sun_ray_'+str(i),g)
    pane('round_amber_sun',ellipse(627,402,151))
    rear=path('M 150 656 L 337 523 L 495 649 L 628 731 L 769 644 L 895 535 L 1110 670 L 1077 882 L 626 1002 L 173 880 Z').intersection(inner)
    main=path('M 348 591 L 629 341 L 856 568 L 794 656 L 709 632 L 652 684 L 576 650 L 500 677 L 425 641 Z')
    maincuts=[[(348,591),(548,450),(629,341)],[(548,450),(578,534),(629,438),(629,341)],[(629,438),(713,486),(856,568)],[(713,486),(711,435)],[(629,438),(665,553),(709,632)],[(578,534),(499,629),(500,677)],[(499,629),(577,594),(665,553)],[(665,553),(794,656)]]
    pane('highest_snow_peak',main,maincuts)
    fore=path('M 147 654 L 338 526 L 455 626 L 548 694 L 665 551 L 805 680 L 896 538 L 1107 671 L 1044 817 L 628 871 L 214 802 Z').intersection(inner)
    # The front ridge is split into its three actual overlapping mountains.
    left=path('M 147 654 L 338 526 L 455 626 L 555 712 L 413 799 L 214 802 Z').intersection(outline.buffer(-12))
    center=path('M 398 747 L 665 551 L 806 680 L 894 749 L 628 867 Z')
    right=mirror(left,623)
    pane('left_foreground_peak',left,[[(147,654),(338,573),(338,526)],[(338,573),(376,660),(455,626)],[(338,573),(292,629)],[(376,660),(413,799)],[(376,660),(448,675),(555,712)]])
    pane('right_foreground_peak',right,[[(1099,654),(908,573),(908,526)],[(908,573),(870,660),(791,626)],[(908,573),(954,629)],[(870,660),(833,799)]])
    pane('central_foreground_peak',center,[[(398,747),(578,592),(665,551)],[(578,592),(590,649),(665,595),(665,551)],[(665,595),(744,651),(806,680)],[(665,595),(641,732),(628,867)],[(590,649),(528,754),(641,732)],[(744,651),(769,747),(894,749)]])
    leftcloud=unary_union([ellipse(282,423,64),ellipse(206,468,47),ellipse(356,467,65),box(160,470,419,504)]).intersection(box(0,0,1254,504))
    rightcloud=affinity.translate(mirror(leftcloud),0,39)
    pane('left_cloud',leftcloud)
    pane('right_cloud',rightcloud)
    hills=[('far_left_hills','M 154 671 C 272 671 424 716 628 779 C 508 821 350 839 192 824 Z'),('far_right_hills','M 1101 675 C 991 676 826 721 628 779 C 764 822 912 841 1068 824 Z'),('lime_rear_meadow','M 382 741 C 472 739 541 761 626 785 C 723 758 804 741 879 745 C 799 791 731 820 626 852 C 521 810 468 784 382 741 Z'),('left_emerald_meadow','M 185 783 C 333 742 497 788 626 852 C 564 874 509 919 487 997 L 302 1039 C 264 965 215 886 185 783 Z'),('right_emerald_meadow','M 1068 783 C 925 742 758 788 626 852 C 688 874 747 919 768 997 L 952 1039 C 995 958 1039 865 1068 783 Z'),('left_lime_meadow','M 358 805 C 442 788 552 829 626 852 C 576 892 550 930 550 969 C 490 896 438 845 358 805 Z'),('right_lime_meadow','M 895 805 C 807 788 705 829 626 852 C 677 892 704 931 704 969 C 768 893 819 845 895 805 Z')]
    foreground_fields=unary_union([path(s) for n,s in hills[3:]])
    for i,(n,s) in enumerate(hills):
        g=path(s).intersection(outline.buffer(-9 if i<3 else -6))
        if n=='lime_rear_meadow':g=g.difference(foreground_fields.buffer(5))
        pane(n,g)
        if n=='lime_rear_meadow':
            d.pieces[-1]['no_clip']=True
            d.pieces[-1]['edge_skip']=shape(foreground_fields.buffer(9))
    stemleft=path('M 318 797 C 319 934 435 1020 577 1090 L 565 1105 C 414 1031 301 942 302 803 Z')
    d.add('left_laurel_branch',stemleft,'Gold',bevel=5,height=.045)
    d.add('right_laurel_branch',mirror(stemleft),'Gold',bevel=5,height=.045)
    def leaf(a,b,width):
        a,b=np.array(a,float),np.array(b,float);delta=b-a;normal=np.array([-delta[1],delta[0]])/np.linalg.norm(delta)
        c1=a+delta*.36+normal*width;c2=a+delta*.72+normal*width*.75
        c3=b-delta*.38-normal*width*.8;c4=a+delta*.22-normal*width*.6
        return path(f'M {a[0]} {a[1]} C {c1[0]} {c1[1]} {c2[0]} {c2[1]} {b[0]} {b[1]} C {c3[0]} {c3[1]} {c4[0]} {c4[1]} {a[0]} {a[1]} Z')
    leaves=[((307,643),(326,835),48),((237,775),(351,921),48),((377,765),(409,958),47),((238,935),(469,1004),48),((355,1046),(561,1078),45)]
    for i,(a,b,w) in enumerate(leaves):
        g=leaf(a,b,w)
        pane('left_laurel_leaf_'+str(i),g)
        pane('right_laurel_leaf_'+str(i),mirror(g))
    pane('bottom_four_point_star',star(627,1013,107,116))
    d.add('outer_gold_setting',outline.difference(outline.buffer(-25)),bevel=8,height=.068)
    d.save()

def teardrop():
    d=Design('sapphire_teardrop','Sapphire Teardrop',626,140,1025)
    outline=path('M 626 140 C 640 139 653 158 674 181 C 828 350 961 542 960 713 C 967 885 823 1025 626 1025 C 428 1025 284 885 290 712 C 290 541 426 349 582 181 C 603 158 613 140 626 140 Z')
    opening=path('M 626 234 C 742 365 889 549 889 708 C 890 843 779 956 626 956 C 473 956 363 844 364 709 C 364 550 510 366 626 234 Z')
    d.add('recessed_blue_gem_seat',opening.buffer(7),'Sapphire',bevel=5,height=.015,base=.09)
    d.add('solid_gold_teardrop_setting',outline.difference(opening),bevel=10,height=.05,base=.24,top=dict(kind='profile',points=[[0,-.035],[9,.025],[18,.055],[28,.055],[38,.02],[50,.02]]))
    d.save()
    # One closed convex gem, with real large facets and no appearance texture.
    angles=np.linspace(0,2*np.pi,64,endpoint=False)
    ring=np.asarray(opening.exterior.coords)[:-1]
    from scipy.spatial import ConvexHull
    # Use a measured pear girdle and the mockup's central six sided table.
    gemoutline=path('M 626 252 C 739 379 875 553 881 704 C 883 834 775 945 626 945 C 480 945 368 835 370 704 C 374 555 515 379 626 252 Z')
    boundary=gemoutline.exterior
    girdle=np.array([boundary.interpolate(t,normalized=True).coords[0] for t in np.linspace(0,1,48,endpoint=False)])
    table=np.array([[626,432],[772,624],[722,782],[626,818],[531,778],[482,624]],float)
    U=d.units;S=U['S']
    points=np.vstack([np.c_[girdle,np.full(len(girdle),.16)],np.c_[girdle,np.full(len(girdle),-.16)],np.c_[table,np.full(len(table),.64)],np.c_[table,np.full(len(table),-.64)]])
    points[:,:2]=np.c_[(points[:,0]-U['axis'])*S,2.995-(points[:,1]-U['top'])*S]
    hull=ConvexHull(points);t=hull.simplices.copy();n=np.cross(points[t[:,1]]-points[t[:,0]],points[t[:,2]]-points[t[:,0]]);bad=(n*hull.equations[:,:3]).sum(1)<0;t[bad]=t[bad,::-1]
    np.savez_compressed(ROOT/d.slug/'gem_geometry.npz',points=points.astype(np.float32),triangles=t.astype(np.int32))
    (ROOT/d.slug/'gem_design.json').write_text(json.dumps(dict(material='CrestGem_Sapphire',no_appearance_texture=True,shared_studio_unchanged=True,front_table_points_px=table.tolist(),approximate_facet_planes=len(np.unique(np.round(hull.equations,5),axis=0))),indent=1)+'\n')

if __name__=='__main__':
    import sys
    for name in sys.argv[1:] or ['campfire','owl','mountain','teardrop']:
        globals()[name]()
