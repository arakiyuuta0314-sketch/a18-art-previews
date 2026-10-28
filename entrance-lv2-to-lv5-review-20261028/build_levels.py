"""A18 entrance level growth: static composites from verified historical independent assets.
Immutable Lv1 and user-approved Lv6 stay in entrance-lv6-review-20261028.
Output is art-review imagery only, not runtime sprites or passage QA.
"""
from pathlib import Path
import hashlib, json, numpy as np, cv2
from PIL import Image

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'entrance-lv6-review-20261028'
LIB=Path(r'C:\Users\User\source\repos\a18-totteoki-museum-pages')
BASE_PATH=SOURCE/'lv1-baseline.png'
END_PATH=SOURCE/'approved-entrance-lv6-20261028.png'
APPROVAL=json.loads((SOURCE/'APPROVED_ENTRANCE_LV6_MANIFEST.json').read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BASE_PATH)==APPROVAL['baselineLevel1Sha256'], 'E_LV1_IMMUTABLE'
assert sha(END_PATH)==APPROVAL['sha256'], 'E_LV6_IMMUTABLE'
BASE=Image.open(BASE_PATH).convert('RGBA')
assert BASE.size==Image.open(END_PATH).size==(1200,880)

def helpers(filename,stop):
    path=SOURCE/filename
    code=path.read_text(encoding='utf-8')
    assert stop in code,(filename,stop)
    namespace={'__name__':'a18_lv2to5_helpers'}
    exec(compile(code[:code.index(stop)],str(path),'exec'),namespace)
    return namespace

placement=helpers('build_existing_placements.py','out={mode:')
extras=helpers('build_extra_ornament_comparison.py',"render('d',False)")
fg=helpers('build_f_g_lv6.py',"output={'F':")
stands=helpers('build_standing_uv.py',"result={'U':")
lush=helpers('build_lush_st.py',"outputs={'S':")
layout=lush['ns']
nop=layout['namespace']

def add_pillars(img,level):
    lights=[('outer_left',0),('outer_right',518),('outer_left',211),('outer_right',335)]
    for side,x in lights:
        for layer in ('emission','body'):
            obj=placement['load']('lighting-additional-sconces-v01',f'fixture_{side}_{layer}.png')
            placement['layer'](img,obj,x,42,28,82,opacity=.9 if layer=='emission' else 1)

def add_sign(img,arrow):
    # Exact U placement/size, built using the existing wooden sign face.
    xy=(181,337) if arrow=='left' else (1002,337)
    stands['put'](img,stands['board'](arrow,59,81),*xy)

def add_reception_lamp(img):
    body,emission=fg['lamp']()
    fg['place'](img,body,36,339,23,41)
    fg['place'](img,emission,38,340,19,26,.9)

def add_long_carpet(img):
    group=LIB/'entrance-carpet-independent-final-20261026'
    tmp=Image.new('RGBA',(235,223))
    for filename,offset in [('entrance_red_carpet_contact_shadow.png',(0,0)),
                            ('entrance_red_carpet_body.png',(0,0)),
                            ('entrance_red_carpet_gold_trim.png',(9,9))]:
        p=group/filename
        assert p.exists(),p
        tmp.alpha_composite(Image.open(p).convert('RGBA'),offset)
    corners=np.float32([[0,0],[234,0],[234,222],[0,222]])
    dest=np.float32([[553,425],[706,425],[779,870],[495,870]])
    m=cv2.getPerspectiveTransform(corners,dest)
    warped=cv2.warpPerspective(np.asarray(tmp),m,(1200,880),
        flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    img.alpha_composite(Image.fromarray(warped,'RGBA'))
    # Preserve real photographed in-game avatar pixels above the floor runner.
    actor=Image.open(LIB/'layout-test/assets/curator-right-00.png').convert('RGBA')
    actor_box=actor.getchannel('A').getbbox()
    mask=actor.crop(actor_box).getchannel('A').resize((60,79),Image.Resampling.LANCZOS)
    img.paste(BASE.crop((661,701,721,780)),(661,701),mask)

def add_gold_frames_and_trim(img):
    src='entrance-frames-independent-20261026'
    l=extras['fetch'](src,'frame_left_original_gold.png')
    r=extras['fetch'](src,'frame_right_original_gold.png')
    for art,rect in ((l,(36,55,159,98)),(r,(367,55,145,98)),(l,(389,251,148,89))):
        _,_,w,h=rect
        extras['paste'](img,extras['gold'](art,(w,h)),rect[0],rect[1])
    for direction,x,w in [('west',45,160),('east',351,154)]:
        trim=fg['source']('entrance-wall-trim-final-20261025',f'entrance_wall_trim_ceiling_{direction}.png')
        fg['place'](img,trim,x,23,w,6,.8)


def add_exhibition_lights(img):
    for name,x,y,w,h in [('entrance_picture_light_west_photo_safe.png',98,33,45,39),
                          ('entrance_picture_light_east_photo_safe.png',408,33,47,39)]:
        lamp=extras['fetch']('entrance-picture-lights-final-20261025',name)
        extras['paste'](img,lamp,x,y,w,h,.94)

def add_lounge_and_counter(img):
    layout['bench'](img,257) # Q-approved image dimensions and feet/armrests
    nop['rear_partition_foliage'](img,'subtle')
    lush['left_tree'](img,'full') # T-approved tall and leafy left tree
    fg['place'](img,fg['clean_flower'](),181,337,27,42)
    fg['draw_ledger'](img)
    fg['reception_medallion'](img)

image_records={}
for level in range(2,6):
    img=BASE.copy()
    add_sign(img,'left')
    add_reception_lamp(img)
    add_long_carpet(img)
    if level>=3:
        add_sign(img,'right')
        add_pillars(img,level)
        add_exhibition_lights(img)
    if level>=4:
        add_gold_frames_and_trim(img)
    if level>=5:
        add_lounge_and_counter(img)
    # Global warm reflection only where golden frames already exist.
    if level>=4:
        img=nop['light_environment'](img,{4:.60,5:.89}[level])
    target=HERE/f'entrance-lv{level}.png'
    img.convert('RGB').save(target,optimize=True)
    rgb=np.asarray(img.convert('RGB'))
    before=np.asarray(BASE.convert('RGB'))
    pixels_changed=int(np.any(rgb!=before,axis=2).sum())
    assert pixels_changed>1000
    image_records[str(level)]={'file':target.name,'width':1200,'height':880,
        'sha256':sha(target),'changed_pixels_vs_Lv1':pixels_changed}
    print('RENDER',level,target.name,pixels_changed,flush=True)

assert sha(BASE_PATH)==APPROVAL['baselineLevel1Sha256']
assert sha(END_PATH)==APPROVAL['sha256']
manifest={
 'schema':'a18-entrance-level-growth-preview/v1',
 'status':'visual proposals for user comparison; Lv2-5 NOT APPROVED',
 'anchors':{'level1':{'source':str(BASE_PATH.relative_to(HERE.parent)),'sha256':sha(BASE_PATH)},
            'level6':{'source':str(END_PATH.relative_to(HERE.parent)),'sha256':sha(END_PATH)}},
 'render_method':'source independent PNG compositing + previously verified screenshot coordinates; baseline and approved images immutable',
 'levels':image_records,
 'cumulative':True,
 'growth':{'2':['standing sign left','reception lamp','long red carpet'],
           '3':['standing sign right','pillar lights 4','picture lights 2'],
           '4':['three golden display frame overlays','wall gold top trim'],
           '5':['257px cushioned bench','tall left tree','rear-right partition foliage','reception accessories'],
           '6':['approved U image only: full right-front planting, foreground plants, ceiling lights, crest, floor accents, final reflectance']},
 'not_validated':['collisions','door transitions','gallery room naming','picture frames portrait/square runtime','live iPhone Safari'],
 'original_art_deletion':False,'game_source_edited':False,
 'merge_authorized':False,
 'source_scripts':[str((SOURCE/n).relative_to(HERE.parent)) for n in (
  'build_existing_placements.py','build_extra_ornament_comparison.py','build_f_g_lv6.py',
  'build_density_k.py','build_planting_nop.py','build_layout_qr.py','build_lush_st.py',
  'build_standing_uv.py')]
}
(HERE/'preview-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('ANCHOR_HASHES_UNCHANGED',sha(BASE_PATH),sha(END_PATH),flush=True)
