from pathlib import Path
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
import json,hashlib
D=Path(__file__).parent
man=json.loads((D/'lush-st-manifest.json').read_text(encoding='utf8'))
assert man['base_q_sha256']==hashlib.sha256((D/'lv6-layout-q.png').read_bytes()).hexdigest()
R={k:Image.open(D/('lv6-lush-'+k.lower()+'.png')).convert('RGB') for k in 'ST'}
for k in 'ST':
 assert R[k].size==(1200,880)
 assert man['outputs'][k]['sha256']==hashlib.sha256((D/('lv6-lush-'+k.lower()+'.png')).read_bytes()).hexdigest()
 assert man['outputs'][k]['planter']['left_edge']==759
 assert man['outputs'][k]['bench']['image_rect']==[793,741,257,65]
Q=Image.open(D/'lv6-layout-q.png').convert('RGB')
# Photo wall, central rug upper zone, and bench top unchanged.
for k in 'ST':
 for crop in [(0,0,1200,436),(794,691,1051,790),(540,436,748,691)]:
  assert ImageChops.difference(Q.crop(crop),R[k].crop(crop)).getbbox() is None,(k,crop)
assert ImageChops.difference(R['S'],R['T']).getbbox() is not None
print('ART_PIXELS_PASS bench and gallery wall preserved, planter extended, trees varied',flush=True)
reports=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for name,w,h,mobile in [('iphone390',390,844,True),('iphone430',430,932,True),('desktop',1200,880,False)]:
  ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
  pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
  result=pg.goto((D/'index.html').as_uri(),wait_until='domcontentloaded')
  assert result.status==200
  assert pg.locator('#tabT').get_attribute('aria-selected')=='true'
  for k,filename in [('Q','lv6-layout-q.png'),('S','lv6-lush-s.png'),('T','lv6-lush-t.png')]:
   pg.locator('#tab'+k).click()
   pg.wait_for_function('(f)=>{const i=document.getElementById("visual");return i.complete&&i.naturalWidth==1200&&i.src.endsWith(f)}',arg=filename,timeout=12000)
   assert pg.locator('#tab'+k).get_attribute('aria-selected')=='true'
  pg.locator('#routes').click();assert pg.locator('#route-overlay').is_visible()
  pg.locator('#zoom').click();assert pg.locator('#stage').evaluate('e=>e.scrollWidth>e.clientWidth')
  assert pg.locator('body').evaluate('e=>e.scrollWidth<=window.innerWidth')
  pg.locator('#zoom').click()
  pg.locator('details.history').first.locator('summary').click()
  for k in ['1','A','B','C','D','E','F','G','H','I','J','K','L','M','X','N','O','P','R']:
   pg.locator('#tab'+k).click()
   assert pg.locator('#tab'+k).get_attribute('aria-selected')=='true'
  assert not errors,errors
  pg.locator('#tabT').click()
  if w==390:
   pg.locator('details.history').first.locator('summary').click()
   pg.screenshot(path=r'C:\Users\User\AppData\Local\Temp\A18_ST_mobile_preview_20261028.png',full_page=True)
  print('BROWSER_PASS',name,flush=True)
  reports.append({'viewport':name,'tab_cases':22,'zoom':'PASS','routes':'PASS','js_errors':0,'horizontal_overflow':False})
  ctx.close()
 browser.close()
(D/'QA_st_results.json').write_text(json.dumps({'status':'PASS','checks':reports},ensure_ascii=False,indent=2),encoding='utf8')
print('ALL_QA_PASS',flush=True)
