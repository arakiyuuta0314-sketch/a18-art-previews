"""Experimental corridor runner (K), based on the exact isolated previous carpet textures.
This file only composes static new candidate; keeps G/H/I/J unchanged.
"""
from pathlib import Path
from PIL import Image
import numpy as np,cv2,json,hashlib
D=Path(r'C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028')
S=Path(r'C:\Users\User\source\repos\a18-totteoki-museum-pages')
G=Path(r'C:\Users\User\source\repos\web-tools-preview\a18\layout-test\assets')
h=Image.open(D/'lv6-density-h.png').convert('RGBA')
lv1=Image.open(D/'lv1-baseline.png').convert('RGBA')
assert h.size==lv1.size==(1200,880)
# Only reinstate actual approved empty floor in the rectangle occupied by the short old rug.
rect=(520,430,748,704)
h.paste(lv1.crop(rect),(rect[0],rect[1]))
# Composite from the actual isolated original carpet, not a newly invented fabric pattern.
group=S/'entrance-carpet-independent-final-20261026'
shadow=Image.open(group/'entrance_red_carpet_contact_shadow.png').convert('RGBA')
body=Image.open(group/'entrance_red_carpet_body.png').convert('RGBA')
trim=Image.open(group/'entrance_red_carpet_gold_trim.png').convert('RGBA')
assert shadow.size==body.size==(235,223)
tmp=Image.new('RGBA',body.size)
tmp.alpha_composite(shadow)
tmp.alpha_composite(body)
tmp.alpha_composite(trim,(9,9))
src=np.array(tmp)
# perspective through the main south walkway: red runner extends to the nearest image edge
corners=np.float32([[0,0],[234,0],[234,222],[0,222]])
dest=np.float32([[553,425],[706,425],[779,870],[495,870]])
M=cv2.getPerspectiveTransform(corners,dest)
warped=cv2.warpPerspective(src,M,(1200,880),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
h.alpha_composite(Image.fromarray(warped,mode='RGBA'))
# Real character in same screenshot orientation and approx same world placement.
spr=Image.open(G/'curator-right-00.png').convert('RGBA')
bounds=spr.getchannel('A').getbbox()
mask=spr.crop(bounds).getchannel('A').resize((60,79),Image.Resampling.LANCZOS)
# Restore pixel colors from the EXACT G snapshot, not a recreated avatar sprite.
# Source and target share the same approved curator pose and world position.
old_avatar=Image.open(D/'lv6-complete-g.png').convert('RGBA').crop((661,701,721,780))
h.paste(old_avatar,(661,701),mask)
out=D/'lv6-density-k.png'
h.convert('RGB').save(out,optimize=True)
data={'status':'visual_comparison_only','purpose':'Would a full length ceremonial runner fill the open floor without additional furniture?',
      'base':'H architectural variant', 'preserved':'G and original sources unchanged',
      'materials':{'body':str(group/'entrance_red_carpet_body.png'),'gold_trim':str(group/'entrance_red_carpet_gold_trim.png'),
                   'shadow':str(group/'entrance_red_carpet_contact_shadow.png'),'actor':str(G/'curator-right-00.png')},
      'image':'lv6-density-k.png','source_to_canvas':dest.tolist(),'photo_or_game_integration':False}
(D/'density-k-manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print('K_GENERATED',hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
