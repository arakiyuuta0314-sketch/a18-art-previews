"""A18 Art preview extras: real extracted signs, exhibition frame materials, and lighting.
Original asset files remain immutable. No game integration. Approval pending.
"""
from pathlib import Path
from PIL import Image
import hashlib,json
src=Path(r"C:\Users\User\source\repos\a18-totteoki-museum-pages")
target=Path(r"C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028")
W,H=1200,880
ox,oy=133,53
sx,sy=934/546,827/483
assets={}
def fetch(folder,name):
 p=src/folder/name
 assert p.exists(),p
 im=Image.open(p).convert("RGBA")
 assets[name]={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':list(im.size)}
 return im
def paste(canvas,im,x,y,w=None,h=None,opacity=1):
 w=im.width if w is None else w
 h=im.height if h is None else h
 pos=(round(ox+x*sx),round(oy+y*sy))
 size=(max(1,round(w*sx)),max(1,round(h*sy)))
 im=im.resize(size,Image.Resampling.LANCZOS)
 if opacity!=1:im.putalpha(im.getchannel('A').point(lambda a:round(a*opacity)))
 canvas.alpha_composite(im,pos)
def gold(src_img, rect):
 # Nine-slice gold frame: keep corner decoration shape and border thickness,
 # stretch only horizontal & vertical edge runs. Source transparent interior.
 im=src_img.crop(src_img.getchannel('A').getbbox())
 ow,oh=im.size
 tw,th=rect[0],rect[1]
 # Golden ornaments: original corner bands 20x22 logical px
 left=min(19,ow//4);top=min(20,oh//4)
 right=left;bottom=top
 img=Image.new("RGBA",(tw,th))
 xcuts=[0,left,ow-right,ow]
 ycuts=[0,top,oh-bottom,oh]
 xdst=[0,left,tw-right,tw]
 ydst=[0,top,th-bottom,th]
 assert tw>left+right and th>top+bottom
 for i in range(3):
  for j in range(3):
   tile=im.crop((xcuts[i],ycuts[j],xcuts[i+1],ycuts[j+1]))
   tile=tile.resize((xdst[i+1]-xdst[i],ydst[j+1]-ydst[j]),Image.Resampling.LANCZOS)
   img.alpha_composite(tile,(xdst[i],ydst[j]))
 return img
def add_signs(canvas):
 folder='entrance-fixtures-final-20261025'
 l=fetch(folder,'entrance_west_sign.png')
 r=fetch(folder,'entrance_east_sign.png')
 # Locate signs under back wall exhibit frames, above furniture,
 # aligned toward the left and right REAR passages.
 paste(canvas,l,56,170,38,37)
 paste(canvas,r,454,170,38,37)
def add_gold_and_lights(canvas):
 folder='entrance-frames-independent-20261026'
 L=fetch(folder,'frame_left_original_gold.png')
 R=fetch(folder,'frame_right_original_gold.png')
 # Outer frame dimensions fitting the NEW Lv1 exhibit windows.
 # They are deliberately not pasted at their old source locations.
 for im,rect in [(L,(36,55,159,98)),(R,(367,55,145,98))]:
  piece=gold(im,(rect[2],rect[3]))
  paste(canvas,piece,rect[0],rect[1])
 # Right partition: preview only; real game uses ratio-dependent frame.
 # Use the extracted source gold frame border without adding a matte or a new photo.
 fr=gold(L,(148,89))
 paste(canvas,fr,389,251)
 p='entrance-picture-lights-final-20261025'
 lampL=fetch(p,'entrance_picture_light_west_photo_safe.png')
 lampR=fetch(p,'entrance_picture_light_east_photo_safe.png')
 paste(canvas,lampL,98,33,45,39,0.94)
 paste(canvas,lampR,408,33,47,39,0.94)
 # Real small ceiling lights: continuous extracted light-strip and its emission.
 ceil='lighting-ceiling-counter-v01'
 body=fetch(ceil,'ceiling_lamp_row_body.png')
 emit=fetch(ceil,'ceiling_lamp_row_emission.png')
 paste(canvas,emit,0,0,546,483,opacity=0.8)
 paste(canvas,body,0,0,546,483)
def render(letter,expanded):
 canvas=Image.open(target/'lv6-existing-c.png').convert('RGBA')
 add_signs(canvas)
 if expanded:add_gold_and_lights(canvas)
 out=target/f'lv6-existing-{letter}.png'
 canvas.convert('RGB').save(out,optimize=True)
 print(letter,str(out),hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
render('d',False)
render('e',True)
(target/'extras-source-manifest.json').write_text(json.dumps({
 'intent':'D adds existing wayfinding signs to accepted candidate C; E adds original golden frames and original lighting components',
 'status':'visual test only, not adopted, coordinate adjustment experiment',
 'existing_C_preserved':True,
 'placements_logical':{
  'west_sign':[56,170,38,37],'east_sign':[454,170,38,37],
  'back_left_frame':[36,55,159,98],'back_right_frame':[367,55,145,98],
  'right_partition_preview_only':[389,251,148,89],
  'left_exhibit_lamp':[98,33,45,39],'right_exhibit_lamp':[408,33,47,39],
  'ceiling_light_origin':[0,0]
 },
 'source_assets':assets,
 'note':'No runtime photo-frame implementation altered; no sign or collision code changed'
},ensure_ascii=False,indent=2),encoding='utf-8')
