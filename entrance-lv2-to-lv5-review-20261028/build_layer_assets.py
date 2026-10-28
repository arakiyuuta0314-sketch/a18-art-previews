"""Keep A18 entrance growth props as independent transparent source-derived layers.
These are screenshot-resolution review assets, not approved game runtime depth/collision sprites.
"""
from pathlib import Path
from PIL import Image
import hashlib,json
D=Path(__file__).resolve().parent
src=(D/'build_levels.py').read_text(encoding='utf8')
mark='image_records={}'
assert mark in src
ns={'__name__':'a18_transparent_layer_helpers','__file__':str(D/'build_levels.py')}
exec(compile(src[:src.index(mark)],str(D/'build_levels.py'),'exec'),ns)
L=D/'layers';L.mkdir(exist_ok=True)
size=(1200,880)
def fresh():return Image.new('RGBA',size,(0,0,0,0))
def left_sign(im):ns['add_sign'](im,'left')
def right_sign(im):ns['add_sign'](im,'right')
def reception_lamp(im):ns['add_reception_lamp'](im)
def bench(im):ns['layout']['bench'](im,257)
def tree(im):ns['lush']['left_tree'](im,'full')
def rear_foliage(im):ns['nop']['rear_partition_foliage'](im,'subtle')
def counter_objects(im):
    f=ns['fg']
    f['place'](im,f['clean_flower'](),181,337,27,42)
    f['draw_ledger'](im)
    f['reception_medallion'](im)
def gold_frames_and_picture_lights(im):ns['add_gold_frames_and_trim'](im)
def picture_lights(im):ns['add_exhibition_lights'](im)
def carpet(im):ns['add_long_carpet'](im)
def pillars(im):ns['add_pillars'](im,3)
steps={
    'lv2-standing-sign-left':(2,left_sign),
    'lv2-reception-lamp':(2,reception_lamp),
    'lv2-carpet':(2,carpet),
    'lv3-pillar-lights':(3,pillars),
    'lv3-picture-lights':(3,picture_lights),
    'lv3-standing-sign-right':(3,right_sign),
    'lv4-gold-frames-picture-lights-and-trim':(4,gold_frames_and_picture_lights),
    'lv5-bench':(5,bench),
    'lv5-left-tall-tree':(5,tree),
    'lv5-rear-right-foliage':(5,rear_foliage),
    'lv5-reception-objects':(5,counter_objects),
}
record={}
for name,(level,fn) in steps.items():
    img=fresh();fn(img)
    bbox=img.getchannel('A').getbbox()
    assert bbox,name
    path=L/(name+'.png');img.save(path,optimize=True)
    record[name]={'fromLevel':level,'file':str(path.relative_to(D)).replace('\\','/'),
        'alphaBounds':list(bbox),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'source':'existing isolated asset composited at approved screenshot coordinates'}
(D/'layer-manifest.json').write_text(json.dumps({
  'schema':'a18-entrance-independent-preview-layers/v1',
  'renderSurface':[1200,880],
  'status':'preview reusable layers; runtime z-order and collision NOT_IMPLEMENTED',
  'existingGameIndependentElements':{
    'background':'layout-test/assets/entrance/approved_initial_20261027/entrance_background_initial_approved.png',
    'counter':'layout-test/assets/entrance/counter_candidate_20261028/reception_lshape_lv1_approved_v11.webp',
    'leftPartition':'layout-test/assets/entrance/counter_candidate_20261028/partition_left_oak_lv1_approved_v11.png',
    'rightPartition':'layout-test/assets/entrance/counter_candidate_20261028/partition_right_lv1_approved_v11.png'},
  'layers':record,'historicalAssetsPreserved':True
},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('INDEPENDENT_LAYERS_PASS',len(record),flush=True)
