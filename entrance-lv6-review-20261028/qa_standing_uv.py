"""A18 standing sign regression and browser render; static preview only."""
from pathlib import Path
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
import hashlib,json
D=Path(__file__).parent
manifest=json.loads((D/'standing-uv-manifest.json').read_text(encoding='utf8'))
for p,sha in manifest['heritage_source_sha256'].items():
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha,p
T=Image.open(D/'lv6-lush-t.png').convert('RGB')
U=Image.open(D/'lv6-standing-u.png').convert('RGB')
V=Image.open(D/'lv6-standing-v.png').convert('RGB')
for name,img in [('U',U),('V',V)]:
 assert img.size==T.size==(1200,880)
 assert hashlib.sha256((D/f'lv6-standing-{name.lower()}.png').read_bytes()).hexdigest()==manifest['variants'][name]['sha256']
 # No modification of any below-partition artwork or people or central carpet.
 for box in [(0,0,1200,330),(133,497,1067,880),(510,350,760,490),(190,150,481,311),(770,147,1012,311)]:
  assert ImageChops.difference(T.crop(box),img.crop(box)).getbbox() is None,(name,box)
 assert ImageChops.difference(T,img).getbbox()
 assert manifest['variants'][name]['west_sign_rect'][0]<220
 assert manifest['variants'][name]['east_sign_rect'][0]>960
print('IMAGE_AND_SOURCE_INTEGRITY_PASS',flush=True)
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for name,w,h,mobile in [('iphone390',390,844,True),('iphone430',430,932,True),('desktop1200',1200,880,False)]:
  ctx=b.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
  pg=ctx.new_page();errors=[]
  pg.on('pageerror',lambda e:errors.append(str(e)))
  r=pg.goto((D/'index.html').as_uri(),wait_until='domcontentloaded',timeout=25000)
  assert r.status==200
  assert pg.locator('#tabU').get_attribute('aria-selected')=='true'
  for k,n in [('T','lv6-lush-t.png'),('U','lv6-standing-u.png'),('V','lv6-standing-v.png')]:
   pg.locator('#tab'+k).click()
   pg.wait_for_function('(f)=>{const e=document.getElementById("visual");return e&&e.complete&&e.naturalWidth===1200&&e.src.endsWith(f)}',arg=n,timeout=15000)
   assert pg.locator('#tab'+k).get_attribute('aria-selected')=='true'
  pg.locator('#routes').click()
  assert pg.locator('#route-overlay').is_visible()
  pg.locator('#zoom').click()
  assert pg.locator('#stage').evaluate('e=>e.scrollWidth>e.clientWidth')
  assert pg.locator('body').evaluate('e=>e.scrollWidth<=window.innerWidth')
  pg.locator('details.history').first.locator('summary').click()
  for k in ['1','A','B','C','D','E','F','G','H','I','J','K','L','M','X','N','O','P','Q','R','S']:
   pg.locator('#tab'+k).click()
   assert pg.locator('#tab'+k).get_attribute('aria-selected')=='true'
  assert not errors,errors
  pg.locator('#tabU').click()
  if w==390:
   pg.locator('details.history').first.locator('summary').click()
   pg.screenshot(path=r'C:\Users\User\AppData\Local\Temp\A18_standing_U_iphone390_qa.png',full_page=True)
  results.append({'viewport':name,'tabs':24,'status':'PASS','js_errors':0,'horizontal_overflow':False})
  print('BROWSER_QA_PASS',name,flush=True)
  ctx.close()
 b.close()
(D/'QA_standing_uv.json').write_text(json.dumps({'status':'PASS','results':results},ensure_ascii=False,indent=2),encoding='utf8')
print('ALL_QA_PASS',flush=True)
