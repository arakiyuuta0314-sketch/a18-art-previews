"""A18 T approved art study: remove wall signs, compare independently layered standing directional signs.
Never edits source/other gallery/game, creates U and V static screenshots only.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
import hashlib,json
D=Path(r'C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028')
R=Path(r'C:\Users\User\source\repos\a18-totteoki-museum-pages\entrance-fixtures-final-20261025')
T=Image.open(D/'lv6-lush-t.png').convert('RGBA')
B=Image.open(D/'lv1-baseline.png').convert('RGBA')
assert T.size==B.size==(1200,880)
paths={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [D/'lv6-lush-t.png',D/'lv1-baseline.png',R/'entrance_west_sign.png',R/'entrance_east_sign.png']}
def remove_wall_signs(scene):
 # Original Lv1's exact geometric wall wood is used for sign-free background.
 # Restore only the two gilded wall plaque regions with a feathered edge.
 areas=[(218,341,305,411),(893,343,982,411)]
 for x1,y1,x2,y2 in areas:
  patch=B.crop((x1,y1,x2,y2))
  mask=Image.new('L',(x2-x1,y2-y1),0)
  dr=ImageDraw.Draw(mask)
  dr.rectangle((5,5,mask.width-5,mask.height-5),fill=255)
  mask=mask.filter(ImageFilter.GaussianBlur(3.0))
  scene.paste(patch,(x1,y1),mask)
 return areas
def board(arrow,width=61,height=85):
 # Reuse real historical arrow from separate transparent sign source,
 # clipping off only the original wall mounted lamp.
 src=Image.open(R/('entrance_west_sign.png' if arrow=='left' else 'entrance_east_sign.png')).convert('RGBA')
 # x=2..37,y=22..54: arrow/gold trim, not original hanging light.
 tile=src.crop((2,23,37 if arrow=='left' else 38,52))
 art=Image.new('RGBA',(width,height))
 dr=ImageDraw.Draw(art)
 # Solid wood frame, warm carved feet and brass trims; its own cast-shadow is
 # handled separately in scene coordinates.
 x0=4; board_top=1;faceW=width-8;faceH=45
 dr.rounded_rectangle((x0,board_top,width-5,board_top+faceH),radius=4,
  fill=(65,36,19,253),outline=(183,122,56,255),width=3)
 dr.line([(8,5),(width-9,5)],fill=(229,167,86,240),width=2)
 # preserve the actual old artwork: scale only arrow tile to central plaque
 plaque=tile.resize((width-20,31),Image.Resampling.LANCZOS)
 art.alpha_composite(plaque,(10,8))
 # feet under board, freestanding with two supports and brass caps.
 for px in (14,width-19):
  dr.polygon([(px-2,faceH-2),(px+4,faceH-2),(px+5,height-7),
              (px+1,height-2),(px-4,height-7)],fill=(90,53,29,255))
  dr.line([(px,faceH-1),(px+1,height-9)],fill=(223,154,76,211),width=2)
  dr.rounded_rectangle((px-6,height-9,px+7,height-4),radius=2,fill=(82,46,25,255),outline=(180,126,67,240),width=2)
 dr.line([(width//2-17,height-13),(width//2+18,height-13)],fill=(99,59,33,255),width=4)
 # a small cap ornament
 dr.ellipse((width//2-3,0,width//2+3,6),fill=(237,189,102,255),outline=(117,75,34,255))
 return art
def put(scene,src,x,y):
 shadow=Image.new('RGBA',scene.size)
 dr=ImageDraw.Draw(shadow)
 dr.ellipse((x-7,y+src.height-13,x+src.width+7,y+src.height+13),fill=(40,27,18,102))
 scene.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(7)))
 scene.alpha_composite(src,(x,y))
def build(label,spacing):
 base=T.copy()
 areas=remove_wall_signs(base)
 if spacing=='edge':
  l=(181,337);r=(1002,337);w,h=59,81
 else:
  l=(197,332);r=(971,332);w,h=61,85
 for direction,xy in [('left',l),('right',r)]:
  sprite=board(direction,w,h)
  put(base,sprite,*xy)
 output=D/f'lv6-standing-{label.lower()}.png'
 base.convert('RGB').save(output,optimize=True)
 return {'file':output.name,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
   'west_sign_rect':[l[0],l[1],w,h],'east_sign_rect':[r[0],r[1],w,h],
   'wall_signs_removed_areas':areas}
result={'U':build('U','edge'),'V':build('V','inset')}
(D/'standing-uv-manifest.json').write_text(json.dumps({
 'status':'static visual compare only, unapproved sign positions',
 'base':'lv6-lush-t.png (no vegetation, bench or carpet edits)',
 'heritage_source_sha256':paths,
 'variants':result,
 'user_intent':'T baseline, independent floor standing directional boards at left/right edges without obstructing rear passage',
 'collision':'not implemented, route still requires physical QA',
 'original_source_mutation':False,'unused_materials':'retain for other galleries'
},ensure_ascii=False,indent=2),encoding='utf-8')
print('RENDERED',result,flush=True)
