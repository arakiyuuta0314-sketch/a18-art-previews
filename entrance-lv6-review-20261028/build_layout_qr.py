"""A18 Level 6 Q/R: compare gallery-frame-width bench/planter and left partition pot.
Built using the historical N/O/P pure helper definitions without running their output pipeline.
All original art and prior visual alternatives remain unchanged.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageEnhance,ImageFilter,ImageChops
import numpy as np,hashlib,json
D=Path(r'C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028')
S=Path(r'C:\Users\User\source\repos\a18-totteoki-museum-pages')
previous=(D/'build_planting_nop.py').read_text(encoding='utf8')
marker='variants={k:build(k) for k in '
assert marker in previous
namespace={'__name__':'a18_nop_helpers'}
exec(compile(previous[:previous.index(marker)],str(D/'build_planting_nop.py'),'exec'),namespace)
K=namespace['canvas0']; O=Image.open(D/'lv6-planting-o.png').convert('RGBA')
assert K.size==O.size==(1200,880)
load=namespace['load']
source_bench=namespace['bench']
image_sha={p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in ('lv6-density-k.png','lv6-planting-o.png')}
def clear_right_pot(scene):
 namespace['clear_original_right_plant'](scene)
def adjust_light(scene):
 return namespace['light_environment'](scene,.89)
def bench(scene,width):
 """One coherent 9-slice. Keep feet/arms original and stretch only central seating.
 Actual downstairs right gold frame outer x~800..1052 width~252.
 """
 original=source_bench.crop(source_bench.getchannel('A').getbbox())
 ow,oh=original.size
 corner=44
 destW,destH=width,65
 side=43
 out=Image.new('RGBA',(destW,destH))
 for tile,x,dw in [(original.crop((0,0,corner,oh)),0,side),
                   (original.crop((corner,0,ow-corner,oh)),side,destW-2*side),
                   (original.crop((ow-corner,0,ow,oh)),destW-side,side)]:
  t=tile.resize((dw,destH),Image.Resampling.LANCZOS)
  out.alpha_composite(t,(x,0))
 out=ImageEnhance.Color(out).enhance(.94)
 x,y=793,741
 # The old bench does not move left, only extends right to echo exhibit width.
 shadow=Image.new('RGBA',scene.size);d=ImageDraw.Draw(shadow)
 d.ellipse((x-10,y+41,x+destW+12,y+79),fill=(30,24,18,82))
 scene.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)))
 scene.alpha_composite(out,(x,y))
 return {'image_rect':[x,y,destW,destH],
         'right_end':x+destW,'frame_right_end_approx':1052,
         '9_slice':'original armrest and legs preserved'}
plantA=namespace['plantA'];plantB=namespace['plantB']
variant=namespace['variant_plant']
def long_planter(scene,width,shift_y=0):
 """Dark wood planting bed at lower foreground: matches bench/picture frame width.
 Leaves are cropped from the two old independent plants, not painted from scratch.
 """
 x=1066-width;y=829+shift_y
 ww=width;hh=46
 wood=namespace['plinth'].crop((0,9,89,48))
 board=Image.new('RGBA',(ww,hh))
 # 9-slice corners to maintain wood endposts and panel edges.
 col=25
 board.alpha_composite(wood.crop((0,0,25,wood.height)).resize((col,hh),Image.Resampling.LANCZOS),(0,0))
 board.alpha_composite(wood.crop((25,0,64,wood.height)).resize((ww-2*col,hh),Image.Resampling.LANCZOS),(col,0))
 board.alpha_composite(wood.crop((64,0,89,wood.height)).resize((col,hh),Image.Resampling.LANCZOS),(ww-col,0))
 shadow=Image.new('RGBA',scene.size); d=ImageDraw.Draw(shadow)
 d.ellipse((x-15,y+19,x+ww+16,min(885,y+hh+14)),fill=(37,23,13,92))
 scene.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
 # Vegetation starts below the feet of the bench, with its first foliage at 807-816.
 centers=list(range(x+16,x+ww-4,25))
 for i,cx in enumerate(centers):
  f=variant(plantA if i%3 else plantB,i+7,.65 if i%4 else .77)
  fy=(y-33)+(i%3)*3
  scene.alpha_composite(f,(cx-f.width//2,fy))
 scene.alpha_composite(board,(x,y))
 # Re-establish a few front leaves over the rim to hide mechanical spacing.
 for i,cx in enumerate(centers[::2]):
  f=variant(plantB if i%2 else plantA,i+27,.44)
  scene.alpha_composite(f,(cx-f.width//2,y-18+(i%2)*2))
 return {'rect':[x,y,ww,hh],'planting_width':ww,'foliage_count':len(centers)}
def left_partition_plant(scene,variant_id):
 # The rightmost end of the LEFT partition is about x=462 at y=420..618.
 # Root near the corner, foliage overlaps the panel end at x~455 but avoids notes/NPC.
 # Use a different original potted plant type than the far-left palm.
 pot=load('layout-test/assets/candidate-v1.1/props/potted_plant.png')
 bbox=pot.getchannel('A').getbbox()
 assert bbox
 pot=pot.crop(bbox)
 data=np.asarray(pot).copy()
 rgb=data[:,:,:3].astype(np.float32)
 # Source vase is blue porcelain; tone only the lower blue-colored ceramic
 # to muted bronze/brown, preserving green foliage. Mask out the bright halo.
 y=np.arange(data.shape[0])[:,None]
 blue=(rgb[:,:,2]>rgb[:,:,0]*1.11)&(rgb[:,:,2]>rgb[:,:,1]*0.97)&(y>=78)
 rgb[blue]=np.clip(rgb[blue]*np.array([1.30,.76,.44])[None,:]+np.array([22,8,-5]),0,255)
 data[:,:,:3]=rgb.astype('uint8')
 a=data[:,:,3].astype(np.float32)
 whites=(rgb[:,:,0]>207)&(rgb[:,:,1]>204)&(rgb[:,:,2]>193)
 a[whites]*=.05
 data[:,:,3]=a.astype('uint8')
 pot=Image.fromarray(data,'RGBA')
 if variant_id=='Q':
  psize=(65,88);position=(450,534)
 else:
  psize=(61,84);position=(453,540)
 pot=pot.resize(psize,Image.Resampling.LANCZOS)
 x,y=position
 # Add a small soft contact shadow behind original pot, under the partition right edge.
 shadow=Image.new('RGBA',scene.size);dr=ImageDraw.Draw(shadow)
 dr.ellipse((x+10,y+68,x+60,y+87),fill=(30,22,13,66))
 scene.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(5)))
 scene.alpha_composite(pot,(x,y))
 return {'rect':[x,y,*psize],'source':'candidate-v1.1/props/potted_plant.png, warm-ceramic color study','role':'opposite visual weight at left partition right endpoint'}
def make(case,width,planter_width):
 scene=K.copy()
 clear_right_pot(scene)
 scene=adjust_light(scene)
 meta={'bench':bench(scene,width),'planter':long_planter(scene,planter_width)}
 namespace['rear_partition_foliage'](scene,'subtle')
 # The left pot is rendered in the front plane, in front of the wood partition corner.
 meta['left_plant']=left_partition_plant(scene,case)
 p=D/('lv6-layout-'+case.lower()+'.png')
 scene.convert('RGB').save(p,optimize=True)
 meta.update({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 print('CREATED',case,meta,flush=True)
 return meta
# Q is requested approximately frame width; R is slightly airy for density comparison.
outputs={'Q':make('Q',257,252),'R':make('R',232,224)}
(D/'layout-qr-manifest.json').write_text(json.dumps({
 'role':'Static A18 Lv6 art concept only, not accepted or in game',
 'source':'K rug + O rear-planting silhouette/light baseline',
 'user_intent':'Bench and lower-right bed each about as wide as right-side display frame; one new left partition endpoint potted plant',
 'right_exhibit_frame_approx':[799,483,1051,635],
 'historical_image_sha256':image_sha,
 'source_hashes':namespace['assets'],
 'outputs':outputs,
 'game_changes':'none','original_files_modified':False,
 'unaccepted_assets_policy':'Existing materials are preserved and deferred for other galleries.'
 },ensure_ascii=False,indent=2),encoding='utf8')
