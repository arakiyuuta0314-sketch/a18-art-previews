"""A18 Lv6 K -> bench and lighting study. Source originals, G/K, game remain immutable."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageEnhance,ImageFilter,ImageOps
import numpy as np,math,json,hashlib
BASE=Path(r'C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028')
LIB=Path(r'C:\Users\User\source\repos\a18-totteoki-museum-pages\layout-test\assets\candidate-v1.1\props')
R=Image.open(BASE/'lv6-density-k.png').convert('RGBA')
assert R.size==(1200,880)
bench_src=LIB/'bench.png'
sofa_src=LIB/'sofa_red.png'
assert bench_src.is_file() and sofa_src.is_file()
input_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/'lv6-density-k.png',bench_src,sofa_src)}
placement={'x':792,'y':745,'w':155,'h':64,'floor':809}
def ground_shadow(img,x=792,y=778,w=155):
 shadow=Image.new('RGBA',R.size,(0,0,0,0))
 d=ImageDraw.Draw(shadow)
 d.ellipse((x-9,y+5,x+w+12,y+39),fill=(33,22,15,118))
 shadow=shadow.filter(ImageFilter.GaussianBlur(9))
 img.alpha_composite(shadow)
def old_bench(img):
 ground_shadow(img)
 im=Image.open(bench_src).convert('RGBA')
 im=im.crop(im.getchannel('A').getbbox())
 im=ImageEnhance.Color(im).enhance(0.91)
 im=ImageEnhance.Contrast(im).enhance(0.96)
 # Existing source is a useful concept, but a visibly lower-res prop than the foyer.
 im=im.resize((155,64),Image.Resampling.LANCZOS)
 img.alpha_composite(im,(792,745))
def refined_bench(img):
 """Museum bench: source bench guides the burgundy seat / gold-trimmed timber design.
 A separate new alpha-only art study; never edits source sprite."""
 ground_shadow(img)
 S=4; W,H=160,80
 art=Image.new('RGBA',(W*S,H*S),(0,0,0,0))
 dr=ImageDraw.Draw(art)
 def rect(q,fill,outline=None,width=1,radius=0):
  q=tuple(int(z*S) for z in q)
  if radius:dr.rounded_rectangle(q,radius=radius*S,fill=fill,outline=outline,width=width*S)
  else:dr.rectangle(q,fill=fill,outline=outline,width=width*S)
 def poly(coords,fill,outline=None,width=1):
  dr.polygon([(round(x*S),round(y*S)) for x,y in coords],fill=fill)
  if outline:dr.line([(round(x*S),round(y*S)) for x,y in coords+[coords[0]]],fill=outline,width=width*S,joint='curve')
 def line(coords,fill,width=1):
  dr.line([(round(x*S),round(y*S)) for x,y in coords],fill=fill,width=max(1,width*S),joint='curve')
 def ellipse(q,fill,outline=None,width=1):
  dr.ellipse(tuple(int(z*S) for z in q),fill=fill,outline=outline,width=width*S)
 # undercarriage and back legs (dark walnut like the entrance counter)
 for x0 in [19,130]:
  poly([(x0,47),(x0+13,47),(x0+11,71),(x0+6,75),(x0+2,71)],(64,35,19,255),(143,93,46,255),2)
  line([(x0+2,50),(x0+4,69)],(215,146,71,175),1)
  ellipse((x0+1,70,x0+10,75),(111,68,32,255))
 # top rails / subtle tufted contours; not a couch, no bulky backrest
 poly([(13,27),(18,18),(35,13),(125,13),(143,19),(147,28),(143,41),(17,41)],
       (77,41,25,255),(203,145,67,255),3)
 line([(18,23),(40,16),(122,16),(143,23)],(246,190,96,220),2)
 # woven red leather cushion back, muted dark burgundy instead of shiny scarlet
 rect((21,24,138,44),(103,39,45,255),(164,91,71,255),2,radius=8)
 for i in range(18,41):
  alpha=int(24*(i-18)/23)
  line([(27,i),(132,i)],(218,109,102,alpha),1)
 # seat cushion top trapezoid with realistic perspective and thickness
 poly([(19,39),(141,39),(151,48),(10,48)],(140,54,60,255),(217,130,100,255),2)
 # subtle fabric highlight
 poly([(24,41),(137,41),(144,45),(18,45)],(192,88,83,114))
 poly([(11,48),(150,48),(145,58),(16,58)],(100,32,35,255),(177,106,68,255),2)
 for yy in [49,52,55]:
  line([(18,yy),(143,yy)],(175,79,69,130 if yy==49 else 72),1)
 # walnut apron, brass rib and carved filigree
 poly([(15,57),(145,57),(140,65),(20,65)],(70,37,20,255),(197,140,69,255),2)
 line([(25,60),(135,60)],(232,174,83,205),1)
 for x0 in [45,80,115]:
  ellipse((x0-5,58,x0+5,64),(102,61,30,235),(210,150,71,180),1)
  line([(x0-3,61),(x0+3,61)],(239,176,87,210),1)
 # front feet with natural splay
 for x0 in [21,131]:
  poly([(x0,63),(x0+9,63),(x0+11,74),(x0+8,78),(x0-1,77)],(73,43,23,255),(182,120,58,255),2)
  line([(x0+3,65),(x0+4,74)],(218,155,83,180),1)
  ellipse((x0-3,75,x0+11,79),(109,65,29,255),(200,143,64,200),1)
 # side moldings/caps
 for x0 in [11,144]:
  line([(x0,45),(x0+5,56),(x0+9,60)],(224,165,75,195),2)
 # slight texture to turn vector into the gallery's painted wood texture
 px=np.array(art,dtype=np.uint8)
 rng=np.random.default_rng(20261028)
 noise=rng.normal(0,2.0,(H*S,W*S,1))
 rgb=px[:,:,:3].astype('float32')
 rgb=np.clip(rgb+noise,0,255).astype('uint8')
 px[:,:,:3]=rgb
 art=Image.fromarray(px,'RGBA')
 art=art.resize((148,74),Image.Resampling.LANCZOS)
 img.alpha_composite(art,(795,739))
def light_environment(img,strength):
 """Physically located diffuse bounce, preserving image details and light-source contours."""
 arr=np.array(img.convert('RGB'),dtype='float32')
 H,W=arr.shape[:2]
 Y,X=np.ogrid[:H,:W]
 intensity=np.zeros((H,W),dtype='float32')
 def glow(cx,cy,sx,sy,a,mask=None):
  nonlocal intensity
  part=np.exp(-0.5*(((X-cx)/sx)**2+((Y-cy)/sy)**2)).astype('float32')*a
  if mask is not None:part*=mask
  intensity[:]+=part
 # Wall sconces on the pillars. Limit contribution to actual wall/cornice/wood regions.
 wall=(Y>=106)&(Y<401)
 for x in (155,519,729,1044):
  glow(x,227,30,86,0.24,wall)
  glow(x,209,70,105,0.052,wall)
 # Two picture lamps cast wide soft pools on wall/frames, not blowout centers
 for x in (336,884):
  glow(x,177,152,107,0.125,(Y>=105)&(Y<330))
 # small ceiling lamps illuminate wooden soffit
 ceiling=(Y>=56)&(Y<129)
 for x in (234,294,370,438,620,815,884,947):
  glow(x,75,50,33,0.085,ceiling)
 # Door cornice and decorative crest catch warm bounced brass
 glow(627,141,94,50,0.070,(X>=534)&(X<=718)&(Y>=101)&(Y<=248))
 # Stronger but broad reflections on the polished stone near the walls
 floor=(Y>=407)&(Y<=870)
 for x,y,sx,sy,a in [
  (292,429,128,47,0.100),(924,429,132,49,0.102),
  (525,460,87,51,0.080),(735,463,84,50,0.077),
  (230,716,120,93,0.080),(907,732,136,97,0.082),
  (533,635,44,150,0.044),(776,634,44,145,0.043)]:
  glow(x,y,sx,sy,a,floor)
 # prevent cross-over onto black app gutters and cream control UI; floor reflection should
 # exclude actual red carpet center for a natural textile (light stays at edges).
 mask=np.zeros((H,W),dtype='float32')
 mask[:,133:1068]=1
 mask[0:53,:]=0
 # Picture and paper interior do not need added glow; their hue must remain unchanged.
 mask[162:311,209:457]=0
 mask[162:311,780:994]=0
 mask[496:610,813:1038]=0
 intensity=np.clip(intensity*mask*strength,0,0.31)
 # Use warm screen-style brightening, preserve wood grain and dark recess.
 warm=np.array([255,214,146],dtype='float32')[None,None,:]
 alpha=intensity[:,:,None]
 lit=arr+(warm-arr)*alpha
 # subtle warm lift more in red/gold than cyan/blue
 lit[:,:,2]=arr[:,:,2]+(lit[:,:,2]-arr[:,:,2])*0.77
 result=img.copy()
 result.paste(Image.fromarray(np.clip(lit,0,255).astype('uint8'),'RGB').convert('RGBA'))
 return result,{'average_light_fraction':round(float(intensity.mean()),5),'max_strength':round(float(intensity.max()),4)}
def save(name,im):
 p=BASE/name;im.convert('RGB').save(p,optimize=True)
 return {'file':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size),'bytes':p.stat().st_size}
l=R.copy();old_bench(l)
m_base,metrics=light_environment(R,1.25)
m=m_base.copy();old_bench(m)
m_plus_base,metric_plus=light_environment(R,1.7)
m_plus=m_plus_base.copy();old_bench(m_plus)
repaint=R.copy();refined_bench(repaint)
outputs={
 'L':save('lv6-l-bench.png',l),
 'M':save('lv6-m-bench-light.png',m),
 'M_plus':save('lv6-mplus-bench-light.png',m_plus),
 'Bench_repaint_study':save('bench-study/lv6-bench-repaint-study.png',repaint)}
data={'status':'visual-preview-not-adopted','source_base':'lv6-density-k.png',
      'candidate_comparison':{'L':'Adjusted original bench at corrected aspect ratio 155x64 and realistic ground shadow; selected for visual compatibility',
      'M':'L with enhanced wall/frame/ceiling and floor reflected light (1.25x)',
      'M_plus':'L with brighter illumination (1.7x) for upper-bound comparison',
      'Bench_repaint_study':'Refabricated hand-drawn style rejected as too planar vs original source'},
      'placement':placement,'illumination':metrics,'illumination_plus':metric_plus,
      'input_sha256':input_hashes,'output':outputs,
      'preservation':'All existing gallery/source files unchanged; this is static preview only. Historical bench remains deferred asset.'}
(BASE/'lm-preview-manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print('RESULT',json.dumps(data['output'],ensure_ascii=True),flush=True)
