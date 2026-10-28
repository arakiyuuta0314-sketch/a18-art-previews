"""Visual art concept N/O/P for A18 Level 6 entrance. No runtime edits.
N: intermediate illumination + wider bench + lower-right planter.
O: N plus restrained greenery behind right partition.
P: O plus a slightly stronger organic spill into the central walkway.
All assets used read-only. BASE K and historical L/M assets kept unchanged.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageEnhance,ImageFilter
import numpy as np
import cv2,hashlib,json
BASE=Path(r'C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028')
LIB=Path(r'C:\Users\User\source\repos\a18-totteoki-museum-pages')
assert (BASE/'lv6-density-k.png').exists()
canvas0=Image.open(BASE/'lv6-density-k.png').convert('RGBA')
clean0=Image.open(BASE/'lv1-baseline.png').convert('RGBA')
assert canvas0.size==clean0.size==(1200,880)
assets={}
def load(rel):
 p=LIB/rel
 assert p.is_file(),p
 assets[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
 return Image.open(p).convert('RGBA')
bench=load('layout-test/assets/candidate-v1.1/props/bench.png')
left=load('entrance-front-plants-final-20261025/entrance_plant_left.png')
right=load('entrance-front-plants-final-20261025/entrance_plant_right.png')
plinth=load('entrance-plinth-final-20261025/entrance_plinth_right.png')
Ksha=hashlib.sha256((BASE/'lv6-density-k.png').read_bytes()).hexdigest()
def clear_original_right_plant(scene):
 # Original K contains an old, duplicated right pot and wooden stand.
 # Restore *only* the original 2026-10-28 Lv1 clean tile in that bottom-right
 # region. A feathered pixel mask avoids creating a rectangular splice.
 ma=Image.new('L',scene.size,0);d=ImageDraw.Draw(ma)
 d.rectangle((909,726,1066,879),fill=255)
 ma=ma.filter(ImageFilter.GaussianBlur(5))
 scene.paste(clean0,(0,0),ma)
def light_environment(scene,factor):
 # Calibrated against build_lm_comparison.py: M=1.25, target=0.88
 rgb=np.asarray(scene.convert('RGB'),dtype=np.float32).copy()
 H,W=rgb.shape[:2];Y,X=np.ogrid[:H,:W]
 f=np.zeros((H,W),dtype=np.float32)
 def glow(cx,cy,sx,sy,amp,region=None):
  g=np.exp(-.5*(((X-cx)/sx)**2+((Y-cy)/sy)**2)).astype(np.float32)*amp
  if region is not None:g*=region
  f[:]+=g
 wall=(Y>=106)&(Y<401)
 for x in (155,519,729,1044):
  glow(x,227,30,86,.24,wall)
  glow(x,209,70,105,.052,wall)
 for x in (336,884):
  glow(x,177,152,107,.125,(Y>=105)&(Y<330))
 for x in (234,294,370,438,620,815,884,947):
  glow(x,75,50,33,.085,(Y>=56)&(Y<129))
 glow(627,141,94,50,.070,(X>=534)&(X<=718)&(Y>=101)&(Y<=248))
 floor=(Y>=407)&(Y<=870)
 for x,y,sx,sy,a in [(292,429,128,47,.100),(924,429,132,49,.102),
  (525,460,87,51,.080),(735,463,84,50,.077),
  (230,716,120,93,.080),(907,732,136,97,.082),
  (533,635,44,150,.044),(776,634,44,145,.043)]:
  glow(x,y,sx,sy,a,floor)
 mask=np.zeros((H,W),dtype=np.float32)
 mask[:,133:1068]=1;mask[:53,:]=0
 for box in [(209,162,457,311),(780,162,994,311),(813,496,1038,610)]:
  x1,y1,x2,y2=box;mask[y1:y2,x1:x2]=0
 intensity=np.clip(f*mask*factor,0,.31)
 warm=np.array([255,214,146],dtype=np.float32)[None,None,:]
 a=intensity[:,:,None]
 out=rgb+(warm-rgb)*a
 out[:,:,2]=rgb[:,:,2]+(out[:,:,2]-rgb[:,:,2])*.77
 return Image.fromarray(np.clip(out,0,255).astype('uint8'),'RGB').convert('RGBA')
def wide_bench(scene):
 # Material is unchanged old bench (wood + burgundy upholstery).
 # Center panel expands by ~30px; armrests/feet are not stretched.
 src=bench.crop(bench.getchannel('A').getbbox())
 ow,oh=src.size
 # 202 wide source -> target 190 wide; restore original proportions at 62 high.
 # 9-slice using full source crop: keep 42px left and right edges incl legs.
 corner=44;mid=ow-2*corner
 destW,destH=194,65
 left_part=src.crop((0,0,corner,oh)).resize((42,destH),Image.Resampling.LANCZOS)
 mid_part=src.crop((corner,0,ow-corner,oh)).resize((destW-84,destH),Image.Resampling.LANCZOS)
 right_part=src.crop((ow-corner,0,ow,oh)).resize((42,destH),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',(destW,destH))
 out.alpha_composite(left_part,(0,0))
 out.alpha_composite(mid_part,(42,0))
 out.alpha_composite(right_part,(destW-42,0))
 out=ImageEnhance.Color(out).enhance(.94)
 # same X as L/M, extend to right (not grow leftward toward carpet)
 x,y=793,742
 shadow=Image.new('RGBA',scene.size)
 dd=ImageDraw.Draw(shadow)
 dd.ellipse((x-10,y+42,x+destW+11,y+79),fill=(30,24,18,90))
 scene.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))
 scene.alpha_composite(out,(x,y))
 return {'rect':[x,y,destW,destH],'source_type':'existing bench stretched only at middle segment'}
def foliage_mask(src,side):
 # Keep only foliage, remove any pot/stand. All source leaves remain source artwork.
 if side=='left':
  bb=(0,7,51,56)
 else:
  bb=(17,9,79,58)
 piece=src.crop(bb).convert('RGBA')
 rgba=np.asarray(piece).copy()
 rgb=rgba[:,:,:3]
 hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
 # Preserve naturally shaded deep and light foliage, exclude most ochre wood,
 # ochre-green stray reflections and terracotta pot.
 mask=cv2.inRange(hsv,np.array([25,26,18],np.uint8),np.array([110,255,255],np.uint8))
 original=rgba[:,:,3]
 mask=np.minimum(mask,original)
 # smooth tiny isolated background pixels while retaining leaf silhouettes
 mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
 mask=cv2.GaussianBlur(mask,(3,3),.45)
 # mild taper at bottom to avoid cropped flat foliage edges
 hh=mask.shape[0]
 for y in range(max(0,hh-9),hh):
  mask[y,:]=(mask[y,:].astype('float32')*max(0,(hh-y-1)/9)).astype('uint8')
 rgba[:,:,3]=mask
 return Image.fromarray(rgba,'RGBA')
plantA=foliage_mask(left,'left')
plantB=foliage_mask(right,'right')
def variant_plant(im,index,scale):
 # Varied source leaf arrangements, no flat duplicate silhouette.
 im=im.copy()
 if index%3==1:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 if index%4==0:im=im.rotate(-7,expand=True,resample=Image.Resampling.BICUBIC)
 elif index%4==2:im=im.rotate(6,expand=True,resample=Image.Resampling.BICUBIC)
 if index%2==0:im=ImageEnhance.Color(im).enhance(.86)
 if index%3==0:im=ImageEnhance.Brightness(im).enhance(.84)
 new=(max(3,round(im.width*scale)),max(3,round(im.height*scale)))
 return im.resize(new,Image.Resampling.LANCZOS)
def planter(scene):
 # A low planted border rather than an identical tall pot.
 # Reuse wooden plinth artwork for texture in a custom compact trough.
 wood=plinth.crop((0,9,89,48))
 trough=wood.resize((100,51),Image.Resampling.LANCZOS)
 # Back row of leaves first, trough on top of bases, front leaves after.
 positions=[(977,793,0,.73),(1006,784,1,.9),(1039,784,2,.85),(1052,800,3,.7)]
 for x,y,k,scale in positions:
  f=variant_plant(plantA if k%2 else plantB,k,scale)
  scene.alpha_composite(f,(x,y))
 # planter has wood panel geometry matched to existing wood and fixed right edge
 shadow=Image.new('RGBA',scene.size);dr=ImageDraw.Draw(shadow)
 dr.ellipse((975,846,1091,887),fill=(27,20,14,102))
 scene.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)))
 scene.alpha_composite(trough,(971,825))
 # small leaves naturally overhanging its upper rail
 for x,y,k,scale in [(979,795,4,.63),(1018,796,5,.74),(1052,804,6,.65)]:
  f=variant_plant(plantB if k%2 else plantA,k,scale)
  # keep only upper silhouette, not full pots
  scene.alpha_composite(f,(x,y))
 return {'planter_rect':[971,784,1100,881],'material':'existing right wooden plinth + independently masked green foliage'}
def rear_partition_foliage(scene,spill):
 # Construction: wall begins around x=770,y=480, slopes to y=469 at x=1067.
 # Greenery is BEHIND the wall. Mask pixels at/under the top edge of the partition,
 # revealing tops of plants and a controlled tiny incursion at the inner corridor.
 overlay=Image.new('RGBA',scene.size)
 # Understory uses the SAME manually-isolated original leaf images, at
 # irregular smaller scales. No synthetic flat-color hedge that could look
 # like a cutout cardboard silhouette.
 rng=np.random.default_rng(410 if spill=='subtle' else 411)
 for i,xx in enumerate(range(771,1080,20 if spill=='subtle' else 16)):
  y0=449+int(rng.integers(-3,6))
  sz=float(rng.uniform(.32,.51))
  spr=variant_plant(plantB if i%3 else plantA,20+i,sz)
  overlay.alpha_composite(spr,(xx-10,y0))
 if spill=='subtle':
  cluster=[(760,432,0,.82),(793,437,1,.89),(841,443,2,.67),
           (918,443,3,.61),(1006,440,4,.77),(1040,442,5,.63)]
  inward=750
 else:
  cluster=[(743,431,0,.93),(779,431,1,1.06),(817,439,2,.89),
           (866,438,3,.73),(930,443,4,.68),(1000,437,5,.9),
           (1042,436,6,.84)]
  inward=734
 for x,y,k,scale in cluster:
  f=variant_plant(plantA if k%2==0 else plantB,k,scale)
  overlay.alpha_composite(f,(x,y))
 # reveal only upper side of the partition. A little reaches into the center-left
 # floor, but no leaves cross the picture, doorway or actual passage.
 pix=np.asarray(overlay,dtype=np.uint8).copy()
 H,W=pix.shape[:2]
 xx,yy=np.meshgrid(np.arange(W),np.arange(H))
 edge=(483-.043*(xx-766))
 # In the corridor overhang, let isolated leaf tips descend a few pixels more.
 limit=np.where(xx>=766,edge-1,486 if spill=='subtle' else 490)
 allowed=(yy<limit)&(yy>=425)&(xx>=inward)&(xx<1068)
 # Protect route + central rug: no organic decor in x<730 or main door.
 pix[:,:,3]=np.where(allowed,pix[:,:,3],0)
 # Add soft floor/wall shadow just under visible leaves (extremely restrained)
 top=Image.fromarray(pix,'RGBA')
 scene.alpha_composite(top)
 return {'variation':spill,'inward_x_min':inward,'wall_top_clip_rule':'y < 483 - 0.043*(x-766)','frame_occlusion':False}
def build(key):
 # Start from exact stable K, do not modify historical variants or source.
 img=canvas0.copy()
 clear_original_right_plant(img)
 img=light_environment(img,.89)
 benchmeta=wide_bench(img)
 plantermeta=planter(img)
 behind=None
 if key=='O':behind=rear_partition_foliage(img,'subtle')
 if key=='P':behind=rear_partition_foliage(img,'visible')
 out=BASE/('lv6-planting-'+key.lower()+'.png')
 img.convert('RGB').save(out,optimize=True)
 print('SAVED',key,str(out),out.stat().st_size,flush=True)
 return {'filename':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bench':benchmeta,
         'front_planter':plantermeta,'rear_growth':behind}
variants={k:build(k) for k in 'NOP'}
man={
 'purpose':'A18 Lv6 static placement options: intermediate L/M lighting, wider bench, low planter instead of duplicate old pot, rear partition foliage.',
 'read_only_baseline_sha256':Ksha,
 'visual_approval':'NOT YET','collision':'NOT IMPLEMENTED','app_code':'NOT TOUCHED',
 'input_sources':assets,'lighting_factor':.89,'legacy_M_factor':1.25,
 'variants':variants,'deferred':'All input artwork kept intact; unused plant/sofa material deferred for other galleries.'}
(BASE/'planting-nop-manifest.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding='utf8')
print('ALL_FINISHED',flush=True)
