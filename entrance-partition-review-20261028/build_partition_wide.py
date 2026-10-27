"""Build an independent wide review-only PNG from v01 approved-geometry candidate.
This is a geometric draft, not an approved final artwork or an alteration to game's assets.
"""
from pathlib import Path
from PIL import Image
import hashlib, json
root=Path(__file__).resolve().parent
original=Image.open(root/'partition.png').convert('RGBA')
assert original.size==(768,528)
wide=original.resize((928,496),Image.Resampling.LANCZOS)
assert wide.getchannel('A').getextrema()==(0,255)
png=root/'partition-wide-v02.png'
webp=root/'partition-wide-v02.webp'
wide.save(png,'PNG',optimize=True)
wide.save(webp,'WEBP',quality=95,method=6,exact=True)
assert Image.open(png).size==Image.open(webp).size==(928,496)
(root/'partition-wide-v02-manifest.json').write_text(json.dumps({
'previous_logical_size':[192,132], 'wide_review_logical_size':[232,124],
'new_render_dimensions':[928,496], 'source_pixels':[768,528],
'status':'review-only independent transparent asset - NOT formally approved',
'transformation':'geometry-only resampling from v01 independent wall; no background composition',
'original_sha256':hashlib.sha256((root/'partition.png').read_bytes()).hexdigest(),
'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),
'webp_sha256':hashlib.sha256(webp.read_bytes()).hexdigest(),
},indent=2,ensure_ascii=False),encoding='utf-8')
print('WIDE_PARTITION_REVIEW',wide.size,png.stat().st_size,webp.stat().st_size)
