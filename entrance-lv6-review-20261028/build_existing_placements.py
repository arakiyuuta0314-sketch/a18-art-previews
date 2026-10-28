"""A18 Lv.6 placement QA: composites ORIGINAL independent sprites over the approved Lv.1 screenshot.
No game/source/background edits. 2026-10-28 art comparison only.
"""
from PIL import Image
from pathlib import Path
import json,hashlib
SRC=Path(r"C:\Users\User\source\repos\a18-totteoki-museum-pages")
DST=Path(r"C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028")
BASE=DST/"lv1-baseline.png"
W,H=1200,880
OX,OY=133,53
SX,SY=934/546,827/483
used={}
def load(group,name):
 p=SRC/group/name
 assert p.is_file(),p
 im=Image.open(p).convert("RGBA")
 used[name]={"source":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size":list(im.size)}
 return im
def coords(x,y,w,h):
 return (round(OX+x*SX),round(OY+y*SY),max(1,round(w*SX)),max(1,round(h*SY)))
def layer(canvas,im,x,y,w=None,h=None,opacity=1):
 if w is None:w=im.width
 if h is None:h=im.height
 px,py,pw,ph=coords(x,y,w,h)
 im=im.resize((pw,ph),Image.Resampling.LANCZOS)
 if opacity!=1:im.putalpha(im.getchannel("A").point(lambda a:round(a*opacity)))
 canvas.alpha_composite(im,(px,py))
def do_render(mode):
 img=Image.open(BASE).convert("RGBA")
 carpet="entrance-carpet-independent-final-20261026"
 sconces="lighting-additional-sconces-v01"
 plants="entrance-front-plants-final-20261025"
 plinths="entrance-plinth-final-20261025"
 # The original photo had a large carpet. Fit its original isolated fibres within the
 # CLEAR passage between the approved wooden partitions. Preserve frame/counter imagery.
 # Keep it behind the player to avoid replacing the actual game sprite.
 x,y,w,h=226,219,131,162
 for name in ["entrance_red_carpet_contact_shadow.png","entrance_red_carpet_body.png"]:
  layer(img,load(carpet,name),x,y,w,h)
 # Gold edge has its OWN verified 173,235 origin, offset relative to original body 164,226.
 trim=load(carpet,"entrance_red_carpet_gold_trim.png")
 layer(img,trim,x+(173-164)*w/235,y+(235-226)*h/223,220*w/235,203*h/223)
 # Four source-extracted body/emission layers. Position on real wooden pilasters.
 for side,x1 in [("outer_left",0),("outer_right",518),("outer_left",211),("outer_right",335)]:
  # Source fixture crop 28 x 82. All four use the verified original alpha, no new lights.
  group="fixture_"+side
  for suffix in ["emission","body"]:
   obj=load(sconces,group+"_"+suffix+".png")
   layer(img,obj,x1,42,28,82,opacity=0.9 if suffix=="emission" else 1)
 if mode in ("B","C"):
  # Two plant sprites are bottom-cut in their source; keep their bases at scene bottom.
  layer(img,load(plants,"entrance_plant_left.png"),0,398)
  layer(img,load(plants,"entrance_plant_right.png"),450,398)
 if mode=="C":
  # Source plinths are also bottom-cut. Put them under those plants at exact bottom anchors.
  for side,x2,y2 in [("left",0,426),("right",457,435)]:
   group="entrance_plinth_"
   shadow=load(plinths,group+"shadow_"+side+".png")
   im=load(plinths,group+side+".png")
   layer(img,shadow,x2,y2)
   layer(img,im,x2,y2)
  # Plants rendered on top of the plinth surfaces, matching original intended layer order.
  layer(img,load(plants,"entrance_plant_left.png"),0,398)
  layer(img,load(plants,"entrance_plant_right.png"),450,398)
 # Restore actual UI overlays on the left from baseline, to prevent the static overlays
 # from appearing ABOVE the touch controls. The UI is always in the foreground.
 # Crop only control button regions, not a large rectangular floor patch.
 raw=Image.open(BASE).convert("RGBA")
 # original buttons in screenshot x10-176,y700-876; most are left of world x133,
 # and this tight region contains the right direction arrow.
 for x1,y1,x2,y2 in [(133,757,174,818)]:
  # Rect is source UI region; no decorations of interest in this segment.
  img.paste(raw.crop((x1,y1,x2,y2)),(x1,y1))
 path=DST/("lv6-existing-"+mode.lower()+".png")
 img.convert("RGB").save(path,optimize=True)
 return {"file":path.name,"size":list(img.size),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
out={mode:do_render(mode) for mode in "ABC"}
record={
 "purpose":"Unapproved visual layout comparison; no new art generated, no game edits",
 "baseline":"lv1-baseline.png from actual Lv1 game screenshot 2026-10-28",
 "coordinate_map":{"logical":[546,483],"screenshot":[1200,880],"game_rect":[133,53,934,827]},
 "variants":{"A":"original carpet + 4 existing pilaster lights","B":"A + original front plants","C":"B + original left/right plinths"},
 "artifacts":out,
 "original_assets":used,
 "decision":"All original assets kept outside game; placement is experimental"
}
(DST/"placement-source-manifest.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
print("OUTPUT",json.dumps(out,ensure_ascii=True),flush=True)
