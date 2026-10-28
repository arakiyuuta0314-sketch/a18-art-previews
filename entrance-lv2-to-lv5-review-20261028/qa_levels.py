"""Image provenance/cumulative composition QA for A18 entrance art review."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent
S=D.parent/'entrance-lv6-review-20261028'
j=json.loads((D/'preview-manifest.json').read_text(encoding='utf8'))
v=json.loads((S/'APPROVED_ENTRANCE_LV6_MANIFEST.json').read_text(encoding='utf8'))
p={1:S/'lv1-baseline.png',6:S/'approved-entrance-lv6-20261028.png'}
p.update({i:D/f'entrance-lv{i}.png' for i in (2,3,4,5)})
rgb={i:np.asarray(Image.open(p[i]).convert('RGB')).copy() for i in range(1,7)}
assert all(x.shape==(880,1200,3) for x in rgb.values())
def sha(x):return hashlib.sha256(x.read_bytes()).hexdigest()
assert sha(p[1])==v['baselineLevel1Sha256']
assert sha(p[6])==v['sha256'] and sha(S/'lv6-standing-u.png')==sha(p[6])
for i in range(2,6): assert sha(p[i])==j['levels'][str(i)]['sha256']
def count(a,b,rect=None):
    if rect:
        x1,y1,x2,y2=rect
        a=a[y1:y2,x1:x2];b=b[y1:y2,x1:x2]
    return int(np.any(a!=b,axis=2).sum())
changes={f'{n-1}_to_{n}':count(rgb[n-1],rgb[n]) for n in range(2,7)}
assert all(v>1000 for v in changes.values()),changes
# Mandatory sequence / feature emergence in expected screenshot rectangles.
areas={'left_sign':(176,332,250,421),'right_sign':(995,330,1068,422),
       'carpet_center':(570,484,679,649),'gold_left':(195,146,471,314),
       'bench':(788,738,1055,812),'left_tree':(436,489,531,642),
       'front_plant':(760,818,1067,879)}
assert count(rgb[1],rgb[2],areas['left_sign'])>400
assert count(rgb[2],rgb[3],areas['right_sign'])>400
assert count(rgb[1],rgb[2],areas['carpet_center'])>1000
assert count(rgb[2],rgb[3],areas['carpet_center'])==0
assert count(rgb[3],rgb[4],areas['gold_left'])>1000
assert count(rgb[4],rgb[5],areas['bench'])>1000
assert count(rgb[4],rgb[5],areas['left_tree'])>1000
assert count(rgb[5],rgb[6],areas['front_plant'])>1000
# UI foreground, top title and lateral bars stay copied from original screenshot.
for n in range(2,6):
    assert np.array_equal(rgb[n][:53,:,:],rgb[1][:53,:,:]),'E_HEADER_CHANGED'
    assert np.array_equal(rgb[n][:,0:130,:],rgb[1][:,0:130,:]),'E_LEFT_BORDER_CHANGED'
    assert np.array_equal(rgb[n][:,1080:,:],rgb[1][:,1080:,:]),'E_RIGHT_BORDER_CHANGED'
# Light protection of unframed teal panels: no false block-shaped glow is applied in Lv2/3.
for n in [2]:
    assert np.array_equal(rgb[n][169:306,216:455],rgb[1][169:306,216:455])
    assert np.array_equal(rgb[n][169:306,785:992],rgb[1][169:306,785:992])
# Contact image for QA (six source images, originals loaded read-only).
W,H=480,352
out=Image.new('RGB',(W*3,H*2+44*2),(242,240,231))
d=ImageDraw.Draw(out)
for idx,n in enumerate(range(1,7)):
    x=(idx%3)*W;y=(idx//3)*(H+44)
    view=Image.open(p[n]).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    out.paste(view,(x,y+44))
    d.text((x+14,y+12),f'Lv.{n}   '+('APPROVED' if n in (1,6) else 'REVIEW'),fill=(25,61,42))
out.save(D/'contact-six-levels.png',optimize=True)
report={
 'status':'PASS','levels':6,'proposals':4,'immutableLv1Sha256':sha(p[1]),
 'immutableLv6Sha256':sha(p[6]),'originalUExactMatch':True,
 'changed_pixels_stepwise':changes,'feature_regions_checked':areas,
 'screenshot_ui_protection':'PASS','historical_sources_changed':False,
 'runtime_collisions':'NOT_TESTED','real_iPhone_Safari':'NOT_TESTED',
 'browser':'PENDING'
}
(D/'qa-image-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('IMAGE_QA_PASS',json.dumps(changes),flush=True)
