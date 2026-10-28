"""A18: spatial density evaluation on top of approved-to-review G image, non-destructive."""
from PIL import Image, ImageDraw,ImageFilter,ImageOps
from pathlib import Path
import json,hashlib,math
BASE=Path(r'C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028')
SRC=Path(r'C:\Users\User\source\repos\a18-totteoki-museum-pages')
orig=Image.open(BASE/'lv6-complete-g.png').convert('RGBA')
assert orig.size==(1200,880)
evidence={}
def load(rel):
 p=SRC/rel
 assert p.is_file(),p
 evidence[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
 return Image.open(p).convert('RGBA')
def real_trim(img):
 # An architectural brass edge beneath the existing large display walls,
 # cut from the already-produced 2026-10-25 wall trim originals.
 west=load('entrance-wall-trim-final-20261025/entrance_wall_trim_wainscot_west.png')
 east=load('entrance-wall-trim-final-20261025/entrance_wall_trim_wainscot_east.png')
 # Position accurately on 2026-10-28 timber front, not the obsolete original layout.
 a=west.resize((311,5),Image.Resampling.LANCZOS)
 b=east.resize((265,5),Image.Resampling.LANCZOS)
 img.alpha_composite(a,(181,328));img.alpha_composite(b,(770,328))
def arch_lighting(img):
 light=Image.new('RGBA',img.size)
 # reflected pools under the two real exhibition lamps, never over photographs.
 # Only within walkable floor, no fake oversized furnishings.
 for cx,cy,rx,ry in [(523,424,62,14),(902,432,137,34),(639,413,96,19)]:
  tile=Image.new('RGBA',(rx*2,ry*2))
  pix=tile.load()
  for y in range(ry*2):
   for x in range(rx*2):
    rr=((x-rx)/rx)**2+((y-ry)/ry)**2
    if rr<1:
     aa=int((1-rr)**2 * (18 if cy>420 else 10))
     pix[x,y]=(240,190,118,aa)
  light.alpha_composite(tile,(cx-rx,cy-ry))
 img.alpha_composite(light)
def floor_brass(img):
 overlay=Image.new('RGBA',img.size)
 d=ImageDraw.Draw(overlay)
 # Slim two-step border, inset from floor edges. Polished mineral inlay not furniture.
 # Against existing tile seams; no continuous rail across the playable center.
 for coords in [[(519,842),(533,842)],[(801,842),(899,842)],[(516,429),(523,440)],[(748,429),(759,440)]]:
  d.line(coords,fill=(170,123,66,110),width=2)
 # A pair of restrained floor rosettes adjacent to but not on the red rug,
 # with a directional diamond motif echoing the existing legacy floor medallions.
 for cx,cy in [(523,580),(743,580)]:
  d.ellipse((cx-8,cy-3,cx+8,cy+3),outline=(167,119,67,112),width=2)
  d.line([(cx-5,cy),(cx+5,cy)],fill=(160,113,63,106),width=1)
 img.alpha_composite(overlay)
def arch_details(img):
 overlay=Image.new('RGBA',img.size)
 d=ImageDraw.Draw(overlay)
 # Small gold joinery at the ends of the rear wood panels, not door or picture frames.
 for cx in [177,499,760,1047]:
  for y in [344,398]:
   d.rounded_rectangle((cx-4,y-3,cx+4,y+3),radius=2,fill=(105,71,40,160),outline=(182,133,64,185),width=1)
 # A subtle floor border along the front of the back wall.
 d.line([(169,407),(501,407)],fill=(178,128,70,82),width=2)
 d.line([(762,407),(1063,407)],fill=(178,128,70,82),width=2)
 img.alpha_composite(overlay)
def build_h():
 img=orig.copy()
 real_trim(img);arch_lighting(img);floor_brass(img);arch_details(img)
 return img
def add_bench(img):
 source=load('layout-test/assets/candidate-v1.1/props/bench.png')
 bbox=source.getchannel('A').getbbox()
 furniture=source.crop(bbox)
 # The legacy sprite is visually a 2D drawn bench. Use near the right wall
 # below the exhibition partition, avoiding corridor behind it.
 size=(151,66)
 small=furniture.resize(size,Image.Resampling.LANCZOS)
 shadow=Image.new('RGBA',(181,45))
 sd=ImageDraw.Draw(shadow)
 sd.ellipse((12,18,168,41),fill=(35,24,13,110))
 img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)),(790,786))
 img.alpha_composite(small,(803,740))
def fit_sample(rel,target_size):
 im=load(rel).convert('RGB')
 # Pad to preserve portrait composition and avoid cropping a visitor's face.
 frame=ImageOps.contain(im,(target_size[0]-10,target_size[1]-10),Image.Resampling.LANCZOS)
 back=Image.new('RGB',target_size,(37,53,41))
 x=(target_size[0]-frame.width)//2;y=(target_size[1]-frame.height)//2
 back.paste(frame,(x,y))
 return back.convert('RGBA')
def add_photos(img):
 # Comparing the experience with artworks is separate from the empty-gallery test.
 # Samples are ONLY illustrative. No user photo or real save data is inserted.
 samples=[
 ('entrance-rear-frames-final-20261025/demo_photo_left.jpg',(215,166,233,130)),
 ('entrance-rear-frames-final-20261025/demo_photo_right.jpg',(781,167,210,128)),
 ]
 for rel,(x,y,w,h) in samples:
  photo=fit_sample(rel,(w,h))
  img.alpha_composite(photo,(x,y))
 # The original right-hand specimen photo is a prior QA scene; use only its
 # inner image crop, without reproducing old trim or player screenshot.
 photo_source=load('entrance-right-handrail-final-20261025/source_photo_03.png')
 # Rectify the 2026-10-25 old perspectively skewed specimen, preserving all source pixels.
 cat=photo_source.transform((96,124),Image.Transform.QUAD,(429,206,429,271,488,325,488,232),Image.Resampling.BICUBIC)
 photo=ImageOps.contain(cat,(215,106),Image.Resampling.LANCZOS)
 region=Image.new('RGBA',(215,106),(36,51,42,255))
 region.alpha_composite(photo,((region.width-photo.width)//2,(region.height-photo.height)//2))
 img.alpha_composite(region,(816,499))
 # A very thin warm internal edge to visually separate matte from gold outer frame.
 dd=ImageDraw.Draw(img)
 for rect in [(212,163,451,298),(778,164,994,298),(813,496,1034,607)]:
  dd.rectangle(rect,outline=(185,142,75,130),width=2)
def save(im,name):
 p=BASE/name;im.convert('RGB').save(p,optimize=True)
 return {'name':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size)}
h=build_h()
i=h.copy();add_bench(i)
j=h.copy();add_photos(j)
outputs={'H':save(h,'lv6-density-h.png'),'I':save(i,'lv6-density-i.png'),'J':save(j,'lv6-density-j.png')}
record={'status':'visual_compare_only','base':'lv6-complete-g.png','variants':{
'H':'G + real wall-trim material / soft lamp pools / brass floor edge / backwall joinery',
'I':'H + existing historical bench in right foreground. Optional; visual compatibility unapproved.',
'J':'H + three historical test photos, purely to estimate visual density when artworks are installed; not actual photo ratio/rendering behavior.'
},'unchanged':['G pixel asset','all source files','Lv1 game','other gallery layouts','artwork slot IDs'],
'source_sha256':evidence,'output':outputs}
(BASE/'density-hij-manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
print('GENERATED',json.dumps(outputs),flush=True)
