"""A18 Lv6 entrance: lush planting concept S/T, based on user-selected Q.
All historical images/source PNG remain unchanged. Only render static comparison.
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import numpy as np, hashlib,json
D=Path(r'C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028')
S=Path(r'C:\Users\User\source\repos\a18-totteoki-museum-pages')
text=(D/'build_layout_qr.py').read_text(encoding='utf8')
cut='# Q is requested approximately frame width;'
assert cut in text
ns={'__name__':'a18_qr_helpers'}
exec(compile(text[:text.index(cut)],str(D/'build_layout_qr.py'),'exec'),ns)
K=ns['K'];loads=ns['load'];orig_hash=hashlib.sha256((D/'lv6-layout-q.png').read_bytes()).hexdigest()
A=ns['plantA'];B=ns['plantB'];v=ns['variant']
def foliage(i,scale=.6):
 base=A if i%3==0 else B
 x=v(base,i+40,scale)
 # vivid but not luminous, varied hue and leaf shape taken from existing source
 if i%4==1:x=ImageEnhance.Brightness(x).enhance(1.09)
 if i%5==3:x=ImageEnhance.Color(x).enhance(1.17)
 return x
def new_planter(scene, lushness):
 x0,y0,ww,hh=759,838,307,37
 wood=ns['namespace']['plinth'].crop((0,9,89,48))
 # bottom wall panel split into fixed ends + repeated center (matches Q version)
 rail=Image.new('RGBA',(ww,hh))
 L,R=25,25
 rail.alpha_composite(wood.crop((0,0,25,wood.height)).resize((L,hh),Image.Resampling.LANCZOS),(0,0))
 rail.alpha_composite(wood.crop((25,0,64,wood.height)).resize((ww-L-R,hh),Image.Resampling.LANCZOS),(L,0))
 rail.alpha_composite(wood.crop((64,0,89,wood.height)).resize((R,hh),Image.Resampling.LANCZOS),(ww-R,0))
 ground=Image.new('RGBA',scene.size);p=ImageDraw.Draw(ground)
 p.ellipse((x0-14,y0+21,x0+ww+13,878),fill=(35,21,11,92))
 scene.alpha_composite(ground.filter(ImageFilter.GaussianBlur(6)))
 # Thick but layered clumps. Keep visible gap to bench 741..806:
 # upper leaves start at 815+, while the bed rim is y=838.
 spacing=19 if lushness=='balanced' else 15
 centers=list(range(x0+13,x0+ww-5,spacing))
 for i,cx in enumerate(centers):
  spr=foliage(i, .67 + (.12 if i%4==0 else 0))
  # keep all tops at or BELOW y=815, no overlap with bench legs
  top=816+(i%4)*3
  # source leaf may be very short, build 2 depths to avoid needle-like grass
  if spr.height>42:spr=spr.resize((spr.width,42),Image.Resampling.LANCZOS)
  scene.alpha_composite(spr,(cx-spr.width//2,top))
 if lushness=='full':
  centers2=list(range(x0+21,x0+ww-14,22))
  for i,cx in enumerate(centers2):
   spr=foliage(i+29,.67)
   scene.alpha_composite(spr,(cx-spr.width//2,823+(i%3)*3))
 scene.alpha_composite(rail,(x0,y0))
 # foliage over the edge, varied clump sizes; no green covering the entire wood front
 centers3=list(range(x0+22,x0+ww-5,26))
 for i,cx in enumerate(centers3):
  spr=foliage(i+62,.40 + (i%3)*.035)
  scene.alpha_composite(spr,(cx-spr.width//2,y0-15+(i%3)*2))
 return dict(rect=[x0,y0,ww,hh],left_edge=x0,carpet_right_edge_approx=760,visible_gap_above_leaves_px=9,foliage_clumps=len(centers)+(len(centers2) if lushness=='full' else 0)+len(centers3))
def left_tree(scene,lushness):
 # Source Q plant (blue pot recoloured warm bronze), with enlarged crown & a
 # high canopy made entirely of historical green leaf crops. Maintain original trunk.
 p=loads('layout-test/assets/candidate-v1.1/props/potted_plant.png')
 p=p.crop(p.getchannel('A').getbbox())
 rgba=np.asarray(p).copy()
 rgb=rgba[:,:,:3].astype(np.float32)
 yy=np.arange(rgba.shape[0])[:,None]
 blue=(rgb[:,:,2]>rgb[:,:,0]*1.11)&(rgb[:,:,2]>rgb[:,:,1]*.97)&(yy>=78)
 rgb[blue]=np.clip(rgb[blue]*np.array([1.30,.76,.44])[None,:]+np.array([22,8,-5]),0,255)
 rgba[:,:,:3]=rgb.astype(np.uint8)
 a=rgba[:,:,3].astype(np.float32)
 white=(rgb[:,:,0]>207)&(rgb[:,:,1]>204)&(rgb[:,:,2]>193)
 a[white]*=.05
 rgba[:,:,3]=a.astype(np.uint8)
 p=Image.fromarray(rgba,'RGBA')
 x0,y0,w,h=(436,497,90,135) if lushness=='balanced' else (433,492,95,143)
 plant=p.resize((w,h),Image.Resampling.LANCZOS)
 sh=Image.new('RGBA',scene.size);d=ImageDraw.Draw(sh)
 d.ellipse((x0+10,y0+h-15,x0+w-2,y0+h+9),fill=(29,19,12,82))
 scene.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
 scene.alpha_composite(plant,(x0,y0))
 # Larger crown centered on top third of a tall and sturdy potted tree.
 # Slightly spill across wood partition end, but never into the carpet or controls.
 cap=7 if lushness=='balanced' else 11
 for i in range(cap):
  cx=x0+int(w*.20)+((i*23)%(int(w*.60)+1))
  y=y0+6+(i%3)*12
  spr=foliage(110+i,.56 + (.11 if lushness=='full' else 0))
  scene.alpha_composite(spr,(cx-spr.width//2,y))
 return dict(rect=[x0,y0,w,h],top=y0,foliage_crowns=cap,may_overlay_left_partition=True)
def make(key,lushness):
 img=K.copy()
 ns['clear_right_pot'](img)
 img=ns['adjust_light'](img)
 bench=ns['bench'](img,257)  # EXACT Q, user approved
 plan=new_planter(img,lushness)
 ns['namespace']['rear_partition_foliage'](img,'subtle')
 tree=left_tree(img,lushness)
 path=D/f'lv6-lush-{key.lower()}.png'
 img.convert('RGB').save(path,optimize=True)
 record=dict(file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
  bench=bench,planter=plan,left_tree=tree,lighting='same as Q',rear_plant='same as O')
 print('CREATED',key,record,flush=True)
 return record
outputs={'S':make('S','balanced'),'T':make('T','full')}
manifest=dict(status='preview only, not game',base='K with Q bench dimensions/light/rear foliage',
 base_q_sha256=orig_hash,
 input_source_sha256=ns['namespace']['assets'] if 'namespace' in ns else {},
 outputs=outputs,game_source_changed=False,
 corridors={'bench_to_picture':'visual clearance remains; actual collisions not implemented',
 'bench_to_planter':'visible light gap, no passage required'},
 unused_assets='preserved for other areas')
(D/'lush-st-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('BUILD_OK',flush=True)
