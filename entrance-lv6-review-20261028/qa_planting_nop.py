"""QA for static N/O/P entrance planting. Protect source assets and historical panels."""
from pathlib import Path
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
import json,hashlib
root=Path(__file__).parent
manifest=json.loads((root/'planting-nop-manifest.json').read_text(encoding='utf8'))
assert manifest['read_only_baseline_sha256']==hashlib.sha256((root/'lv6-density-k.png').read_bytes()).hexdigest()
src=Path(r'C:\Users\User\source\repos\a18-totteoki-museum-pages')
for rel,sha in manifest['input_sources'].items():
 assert hashlib.sha256((src/rel).read_bytes()).hexdigest()==sha,rel
views={}
for key in 'NOP':
 p=root/f'lv6-planting-{key.lower()}.png'
 assert p.exists() and p.stat().st_size>200000
 assert hashlib.sha256(p.read_bytes()).hexdigest()==manifest['variants'][key]['sha256']
 views[key]=Image.open(p).convert('RGB')
 assert views[key].size==(1200,880)
# Adding rear foliage O and P must not alter floor, UI, gold picture frame or people.
for key in 'OP':
 delta=ImageChops.difference(views['N'],views[key]).convert('L')
 bbox=delta.getbbox()
 assert bbox is not None and bbox[0]>=730 and bbox[1]>=425 and bbox[2]<=1068 and bbox[3]<=491,(key,bbox)
 print('FOLIAGE_DIFF_BBOX',key,bbox,flush=True)
# P can show more growth into the corridor than O; both avoid the carpet and photo pane.
assert ImageChops.difference(views['O'],views['P']).getbbox()
for key in 'NOP':
 for box in [(0,0,1200,52),(185,148,465,313),(770,148,1011,313),(810,491,1050,640),(525,495,759,830)]:
  # Root before plant/bench/light still has frame/center route mostly unchanged,
  # but N/O/P mutually must have identical pixels in these protected zones.
  assert ImageChops.difference(views['N'].crop(box),views[key].crop(box)).getbbox() is None,(key,box)
print('ASSET_AND_IMAGE_QA_PASS',flush=True)
reports=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for name,w,h,mobile in [('iphone390',390,844,True),('iphone430',430,932,True),('desktop',1200,880,False)]:
  ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
  page=ctx.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  response=page.goto((root/'index.html').as_uri(),wait_until='domcontentloaded',timeout=30000)
  assert response.status==200
  assert page.locator('#tabO').get_attribute('aria-selected')=='true'
  assert page.locator('details.history').first.get_attribute('open') is None
  for key in ['N','O','P']:
   page.locator('#tab'+key).click()
   f=f'lv6-planting-{key.lower()}.png'
   page.wait_for_function('(filename)=>{let e=document.getElementById("visual");return e.complete&&e.naturalWidth==1200&&e.src.endsWith(filename)}',arg=f,timeout=15000)
   assert page.locator('#tab'+key).get_attribute('aria-selected')=='true'
  page.locator('#tabO').click()
  page.locator('#routes').click()
  assert page.locator('#route-overlay').is_visible()
  page.locator('#zoom').click()
  assert page.locator('#stage').evaluate('e=>e.scrollWidth>e.clientWidth')
  page.locator('#zoom').click()
  assert page.locator('body').evaluate('e=>e.scrollWidth<=window.innerWidth')
  page.locator('details.history').first.locator('summary').click()
  for key in ['1','A','B','C','D','E','F','G','H','I','J','K','L','M','X']:
   page.locator('#tab'+key).click()
   assert page.locator('#tab'+key).get_attribute('aria-selected')=='true'
  assert not errors,errors
  page.locator('#tabO').click()
  if w==390:
   page.locator('details.history').first.locator('summary').click()
   page.screenshot(path=r'C:\Users\User\AppData\Local\Temp\A18_NOP_iphone390_qa.png',full_page=True)
  print('BROWSER_PASS',name,flush=True)
  reports.append({'viewport':name,'tab_count':18,'zoom':'PASS','passage_layer':'PASS','js_errors':0,'overflow':False})
  ctx.close()
 browser.close()
(root/'QA_nop_results.json').write_text(json.dumps({'status':'PASS','checks':reports},ensure_ascii=False,indent=2),encoding='utf8')
print('ALL_NOP_QA_PASS',flush=True)
