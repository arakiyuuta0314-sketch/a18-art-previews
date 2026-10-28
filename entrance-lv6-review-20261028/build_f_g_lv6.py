"""A18 entrance Lv6 art exploration F/G, using actual independent PNGs and small original graphic accents.
Creates static review images only. Does not modify game, source props, or originals.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import json, hashlib, math
R=Path(r"C:\Users\User\source\repos\a18-totteoki-museum-pages")
D=Path(r"C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028")
O=(133,53); S=(934/546,827/483)
orig={}
def source(sub,name):
 p=R/sub/name
 assert p.is_file(),p
 orig[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 return Image.open(p).convert("RGBA")
def world(x,y,w,h):
 return [round(O[0]+x*S[0]),round(O[1]+y*S[1]),max(1,round(w*S[0])),max(1,round(h*S[1]))]
def place(base,im,x,y,w=None,h=None,alpha=1.0):
 if w is None:w=im.width
 if h is None:h=im.height
 xx,yy,ww,hh=world(x,y,w,h)
 p=im.resize((ww,hh),Image.Resampling.LANCZOS)
 if alpha!=1:p.putalpha(p.getchannel('A').point(lambda a:round(a*alpha)))
 base.alpha_composite(p,(xx,yy))
 return [xx,yy,ww,hh]
def crop_alpha(im):
 b=im.getchannel("A").getbbox()
 assert b
 return im.crop(b)
def clean_flower():
 im=source('entrance-counter-flower-final-20261025','entrance_counter_flower_vase.png')
 mask=source('entrance-counter-flower-final-20261025','entrance_counter_flower_alpha_mask.png')
 assert im.size==mask.size
 # Historical PNG contains old counter pixels outside the silhouette. Use the
 # original artist's white alpha mask, not its opaque RGB perimeter.
 a=mask.convert('L')
 im.putalpha(a.point(lambda x:255 if x>=225 else max(0,round(x*1.06))))
 return im
def lamp():
 sub='lighting-ceiling-counter-v01'
 return crop_alpha(source(sub,'counter_lamp_body.png')),crop_alpha(source(sub,'counter_lamp_emission.png'))
def gold_crest(base,grand):
 # Small original vector accent, tightly constrained to solid wood ABOVE the doorway.
 emblem=Image.new('RGBA',(360,145))
 di=ImageDraw.Draw(emblem)
 cx,cy=180,77
 # warm dark recess and gilded oval cartouche
 di.ellipse((98,15,262,135),fill=(41,25,16,214),outline=(172,117,51,235),width=5)
 di.ellipse((113,27,247,122),fill=(83,51,29,220),outline=(241,185,84,250),width=5)
 di.ellipse((125,37,235,112),outline=(148,104,49,190),width=4)
 # stylized museum book + leaf, no text or invented venue name
 di.arc((148,45,211,108),190,351,fill=(224,179,91,235),width=6)
 di.line((180,52,180,100),fill=(236,193,112,255),width=6)
 di.line((145,64,168,73,180,92),fill=(242,205,128,240),width=5,joint='curve')
 di.line((215,64,192,73,180,92),fill=(242,205,128,240),width=5,joint='curve')
 for sign in [-1,1]:
  di.arc((70 if sign<0 else 237,41,122 if sign<0 else 289,117),52 if sign<0 else 128,310 if sign<0 else 246,fill=(198,146,71,210),width=4)
  for n in range(3):
   ex=cx+sign*(58+n*19)
   ey=cy+(-12+n*8)
   di.ellipse((ex-7,ey-7,ex+7,ey+7),fill=(225,174,81,220))
 if grand:
  di.ellipse((174,9,186,21),fill=(250,204,112,245))
  di.arc((75,2,285,140),202,338,fill=(213,159,78,180),width=4)
 emblem=emblem.resize((73 if grand else 62,29 if grand else 25),Image.Resampling.LANCZOS)
 # exact screenshot pixel placement, upper wood between center columns:
 px=round(626-emblem.width/2);py=102
 base.alpha_composite(emblem,(px,py))
 return [px,py,emblem.width,emblem.height]
def draw_ledger(base):
 # Small leather visitor register on the countertop (original vector accent).
 high=3
 art=Image.new('RGBA',(170,66))
 dr=ImageDraw.Draw(art)
 dr.ellipse((7,45,165,64),fill=(24,15,8,80))
 dr.polygon([(16,15),(76,6),(155,18),(94,31)],fill=(66,41,25,255))
 dr.polygon([(20,10),(77,5),(88,34),(21,39)],fill=(238,214,163,255),outline=(135,92,54,255))
 dr.polygon([(77,5),(150,9),(151,38),(88,34)],fill=(244,229,192,255),outline=(135,92,54,255))
 dr.line([(84,8),(89,34)],fill=(149,94,52,240),width=3)
 for j in range(3):
  dr.line([(32,17+6*j),(66,14+6*j)],fill=(165,145,116,160),width=2)
  dr.line([(102,16+6*j),(138,20+5*j)],fill=(165,145,116,150),width=2)
 dr.line([(112,2),(153,20)],fill=(140,92,47,220),width=3)
 dr.ellipse((110,0,116,6),fill=(246,204,124,235))
 # physically small: 23x10 logical, on counter's flat tabletop
 return place(base,art,100,366,28,13,0.95)
def reception_medallion(base):
 # understated mounted escutcheon centered on the FRONT wooden counter panel.
 W,H=72,52
 im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
 d.ellipse((11,4,61,48),fill=(60,37,21,230),outline=(174,115,56,240),width=4)
 d.ellipse((18,10,54,42),outline=(245,194,106,200),width=2)
 d.line([(36,15),(36,37)],fill=(223,169,80,245),width=3)
 d.arc((22,14,48,40),15,165,fill=(232,184,95,235),width=2)
 d.arc((22,14,48,40),195,345,fill=(232,184,95,235),width=2)
 # x=266, y=409 on counter front; avoid butler and character
 return place(base,im,103,413,28,20,0.88)
def floor_motifs(base):
 # Two restrained brass medallions in spare floor outside the carpet and walking path.
 over=Image.new('RGBA',base.size);d=ImageDraw.Draw(over)
 for cx,cy in [(548,797),(813,797)]:
  d.ellipse((cx-14,cy-6,cx+14,cy+6),outline=(159,112,66,116),width=2)
  d.line([(cx-8,cy),(cx+8,cy)],fill=(176,117,56,110),width=2)
  d.ellipse((cx-3,cy-3,cx+3,cy+3),fill=(181,128,67,118))
 return Image.alpha_composite(base,over)
def build(variant):
 assert variant in ('F','G')
 base=Image.open(D/'lv6-existing-e.png').convert('RGBA')
 positions={}
 for name,x,y,w,h in [
  ('west_ceiling',45,23,160,6),
  ('east_ceiling',351,23,154,6)]:
  im=source('entrance-wall-trim-final-20261025','entrance_wall_trim_ceiling_'+('west' if name.startswith('west') else 'east')+'.png')
  positions[name]=place(base,im,x,y,w,h,0.8)
 positions['crest']=gold_crest(base,variant=='G')
 lbody,lemit=lamp()
 # Both cropped PNGs use their natural independent masks; align their actual alpha
 # bbox centers (the full input emission mask has an offset relative to body).
 positions['desk_lamp_body']=place(base,lbody,36,339,23,41)
 positions['desk_lamp_emission']=place(base,lemit,38,340,19,26,0.9)
 vase=clean_flower()
 positions['flower']=place(base,vase,181,337,27,42)
 if variant=='G':
  positions['visitor_ledger']=draw_ledger(base)
  # Mounted counter badge not part of the official base.
  positions['reception_badge']=reception_medallion(base)
  base=floor_motifs(base)
 final=D/('lv6-complete-'+variant.lower()+'.png')
 base.convert('RGB').save(final,optimize=True)
 print('RENDER',variant,final.name,positions,flush=True)
 return {'file':final.name,'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'positions':positions}
output={'F':build('F'),'G':build('G')}
doc={'kind':'A18 Lv6 decorative concept images, unapproved',
     'source_base':'lv6-existing-e.png',
     'variants':{'F':'E + historical reception lamp / historical vase masked + historical beam trim + bespoke small door crest',
                 'G':'F + visitor ledger, counter mounted medallion and two brass floor motifs'},
     'assets_reused':orig,
     'output':output,
     'unchanged':['approved Lv1 source imagery','original independent PNG sources','frame IDs','NPC/collision/game logic'],
     'deferred_policy':'Every source stays preserved; unsuitable entrance assets are deferred for other rooms; never delete originals.'}
(D/'extras-fg-manifest.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
print('COMPLETE',flush=True)
