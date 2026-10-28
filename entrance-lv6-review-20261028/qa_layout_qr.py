from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
import hashlib,json
D=Path(__file__).parent
m=json.loads((D/'layout-qr-manifest.json').read_text(encoding='utf-8'))
for name,sha in m['historical_image_sha256'].items():
 assert hashlib.sha256((D/name).read_bytes()).hexdigest()==sha,name
O=Image.open(D/'lv6-planting-o.png').convert('RGB')
imgs={'Q':Image.open(D/'lv6-layout-q.png').convert('RGB'),'R':Image.open(D/'lv6-layout-r.png').convert('RGB')}
for key,im in imgs.items():
 assert im.size==O.size==(1200,880)
 item=m['outputs'][key]
 assert hashlib.sha256((D/item['file']).read_bytes()).hexdigest()==item['sha256']
 assert item['bench']['image_rect'][2]==(257 if key=='Q' else 232)
 assert item['planter']['planting_width']==(252 if key=='Q' else 224)
 assert item['bench']['image_rect'][0]==793
 # In Q/R all of the artwork and rear-planting above the furniture must remain
 # the same as O. Corrected left pot should only affect left-front partition zone.
 for rect in [(5,5,1195,410),(525,435,753,870),(760,435,1067,718),(182,447,442,590)]:
  assert ImageChops.difference(im.crop(rect),O.crop(rect)).getbbox() is None,(key,rect)
 print('IMAGE_GEOMETRY_QA_PASS',key,item['bench']['image_rect'],item['planter']['rect'],flush=True)
records=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for label,w,h,mobile in [('iphone390',390,844,True),('iphone430',430,932,True),('pc',1200,880,False)]:
  ctx=b.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
  pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
  res=pg.goto((D/'index.html').as_uri(),wait_until='domcontentloaded')
  assert res.status==200
  assert pg.locator('#tabQ').get_attribute('aria-selected')=='true'
  for key,imfile in [('O','lv6-planting-o.png'),('Q','lv6-layout-q.png'),('R','lv6-layout-r.png')]:
   pg.locator('#tab'+key).click()
   pg.wait_for_function('(s)=>{const i=document.getElementById("visual");return i&&i.complete&&i.naturalWidth==1200&&i.src.endsWith(s)}',arg=imfile,timeout=15000)
   assert pg.locator('#tab'+key).get_attribute('aria-selected')=='true'
  pg.locator('#routes').click()
  assert pg.locator('#route-overlay').is_visible()
  pg.locator('#zoom').click()
  assert pg.locator('#stage').evaluate('e=>e.scrollWidth>e.clientWidth')
  assert pg.locator('body').evaluate('e=>e.scrollWidth<=window.innerWidth')
  pg.locator('#zoom').click();pg.locator('#routes').click()
  pg.locator('details.history').first.locator('summary').click()
  for key in ['1','A','B','C','D','E','F','G','H','I','J','K','L','M','X','N','P']:
   pg.locator('#tab'+key).click()
   assert pg.locator('#tab'+key).get_attribute('aria-selected')=='true',key
  assert not errors,errors
  if label=='iphone390':
   pg.locator('#tabQ').click()
   pg.locator('details.history').first.locator('summary').click()
   pg.screenshot(path=r'C:\Users\User\AppData\Local\Temp\A18_QR_390_review_20261028.png',full_page=True)
  records.append({'viewport':label,'tabs':20,'routes':'PASS','zoom':'PASS','overflow':False,'js_errors':0})
  print('BROWSER_QA_PASS',label,flush=True)
  ctx.close()
 b.close()
(D/'QA_qr_results.json').write_text(json.dumps({'result':'PASS','screens':records,'baseline_O_sha256':m['historical_image_sha256']['lv6-planting-o.png']},ensure_ascii=False,indent=2),encoding='utf8')
print('ALL_QR_QA_PASS',flush=True)
