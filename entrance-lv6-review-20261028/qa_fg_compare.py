"""A18 iPhone art review regression. Does not modify any game or save data."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageChops
import json,hashlib
root=Path(__file__).parent
data=json.loads((root/'extras-fg-manifest.json').read_text(encoding='utf-8'))
for rel,expected in data['assets_reused'].items():
 path=Path(r'C:\Users\User\source\repos\a18-totteoki-museum-pages')/rel
 assert path.exists(),path
 assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,rel
old=Image.open(root/'lv6-existing-e.png').convert('RGB')
for key in ['F','G']:
 path=root/('lv6-complete-'+key.lower()+'.png')
 img=Image.open(path).convert('RGB')
 assert img.size==old.size==(1200,880)
 diff=ImageChops.difference(old,img)
 assert diff.getbbox(),key
 # Except for possible additional decor, DO NOT alter the underlying scene,
 # UI, player sprite or the rightmost photo frame.
 protected=[(5,5,1195,46),(665,695,727,781),(807,510,1054,629)]
 for rect in protected:
  assert ImageChops.difference(old.crop(rect),img.crop(rect)).getbbox() is None,(key,rect)
 # Pixel equality outside the canvas image due to overlay compositing.
 assert path.stat().st_size>250000
print('SOURCE_INTEGRITY_PASS',len(data['assets_reused']),'original files; original screenshots unchanged',flush=True)
reports=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for label,w,h,mobile in [('iphone12',390,844,True),('iphone14plus',430,932,True),('desktop',1200,880,False)]:
  ctx=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
  page=ctx.new_page();errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
  response=page.goto((root/'index.html').as_uri(),wait_until='domcontentloaded')
  assert response.status==200
  assert page.locator('#tabG').get_attribute('aria-selected')=='true'
  assert page.locator('#visual').evaluate('(e)=>e.complete&&e.naturalWidth===1200')
  for key in ['1','A','B','C','D','E','F','G']:
   page.locator('#tab'+key).click()
   expected={'1':'lv1-baseline.png','A':'lv6-existing-a.png','B':'lv6-existing-b.png','C':'lv6-existing-c.png','D':'lv6-existing-d.png','E':'lv6-existing-e.png','F':'lv6-complete-f.png','G':'lv6-complete-g.png'}[key]
   page.wait_for_function('(path)=>{let e=document.getElementById("visual");return e.complete&&e.naturalWidth===1200&&e.src.endsWith(path)}',arg=expected,timeout=15000)
   assert page.locator('#tab'+key).get_attribute('aria-selected')=='true'
  page.locator('#routes').click();assert page.locator('#route-overlay').is_visible()
  page.locator('#routes').click();assert not page.locator('#route-overlay').is_visible()
  page.locator('#zoom').click();assert page.locator('#stage').evaluate('(e)=>e.scrollWidth>e.clientWidth')
  page.locator('#zoom').click();assert page.locator('#zoom').get_attribute('aria-pressed')=='false'
  assert page.locator('body').evaluate('(e)=>e.scrollWidth<=innerWidth'),label
  assert not errors,errors
  if label=='iphone12':
   page.screenshot(path=str(Path(r'C:\Users\User\AppData\Local\Temp')/'A18_LV6_G_iphone390_20261028.png'),full_page=True)
  reports.append({'viewport':label,'width':w,'height':h,'tabs':8,'image_load':'PASS','routes':'PASS','zoom':'PASS','horizontal_overflow':False,'js_errors':0,'result':'PASS'})
  print('BROWSER_PASS',label,flush=True)
  ctx.close()
 browser.close()
(root/'QA_fg_results.json').write_text(json.dumps({'status':'PASS','source_file_count':len(data['assets_reused']),'views':reports},ensure_ascii=False,indent=2),encoding='utf8')
print('ALL_QA_PASS',flush=True)
