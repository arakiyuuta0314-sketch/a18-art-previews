from pathlib import Path
d=Path(r'C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv2-to-lv5-review-20261028')
p=d/'build_levels.py'
s=p.read_text(encoding='utf8')
s=s.replace("    lights=[('outer_left',0),('outer_right',518)]\n    if level>=3: lights += [('outer_left',211),('outer_right',335)]","    lights=[('outer_left',0),('outer_right',518),('outer_left',211),('outer_right',335)]")
s=s.replace("    add_pillars(img,level)\n    add_sign(img,'left')\n    add_reception_lamp(img)\n    if level>=3:\n        add_sign(img,'right')\n        add_long_carpet(img)\n    if level>=4:\n        add_gold_and_exhibition_lights(img)","    add_sign(img,'left')\n    add_reception_lamp(img)\n    add_long_carpet(img)\n    if level>=3:\n        add_sign(img,'right')\n        add_pillars(img,level)\n        add_exhibition_lights(img)\n    if level>=4:\n        add_gold_frames_and_trim(img)")
start=s.index('def add_gold_and_exhibition_lights(img):')
end=s.index('\ndef add_lounge_and_counter(img):',start)
block=s[start:end]
a=block.index('    for name,x,y,w,h in')
s=s[:start]+block[:a].replace('def add_gold_and_exhibition_lights','def add_gold_frames_and_trim')+block[block.index('    for direction,x,w in'):]+ '\n\ndef add_exhibition_lights(img):\n'+block[a:block.index('    for direction,x,w in')]+s[end:]
s=s.replace("    # Avoid unframed teal wall rectangles in Lv2/3: the historic warm-light\n    # mask was tailored to the golden framed wall, which begins only in Lv4.\n    # Existing independent pillar bulbs/desk lamp already glow at Lv2/3.","    # Global warm reflection only where golden frames already exist.")
s=s.replace("'2':['standing sign left','outer pillar lights 2','reception lamp'],\n           '3':['standing sign right','inner pillar lights 2','long red carpet'],\n           '4':['three golden display frame overlays','picture lights 2','wall gold top trim']","'2':['standing sign left','reception lamp','long red carpet'],\n           '3':['standing sign right','pillar lights 4','picture lights 2'],\n           '4':['three golden display frame overlays','wall gold top trim']")
p.write_text(s,encoding='utf8')
html=d/'index.html'
h=html.read_text(encoding='utf8')
h=h.replace('左の立て看板／外側の柱灯2灯／受付ランプ。','左の立て看板／受付ランプ／ロング絨毯。')
h=h.replace('右の立て看板／中央寄りの柱灯2灯／ロング絨毯。','右の立て看板／柱灯4灯／展示灯2灯。')
h=h.replace('3か所の金装飾額縁／展示灯2灯／壁上部の金装飾。','3か所の金装飾額縁／壁上部の金装飾。')
h=h.replace('Lv2、左の自立看板、外側の柱灯2灯、受付ランプ','Lv2、左の自立看板、受付ランプ、ロング絨毯')
h=h.replace('Lv3、左右の自立看板と4灯の柱灯、長い中央絨毯','Lv3、左右の自立看板と4灯の柱灯、展示灯2灯')
h=h.replace('Lv4、3か所の金装飾額縁と展示灯、金の梁飾り','Lv4、3か所の金装飾額縁と金の梁飾り')
h=h.replace('左通路が開放され、最初の案内がつきます。','左通路が開放され、中央に絨毯が敷かれます。')
h=h.replace('右通路も開放され、中央の奥行きが生まれます。','右通路も開放され、展示照明が増えます。')
html.write_text(h,encoding='utf8')
print('PATCHED_NEW_DISTRIBUTION')
