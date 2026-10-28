from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
import hashlib,json
root=Path(__file__).parent
prior=json.loads((root/'extras-fg-manifest.json').read_text(encoding='utf8'))
assert hashlib.sha256((root/'lv6-complete-g.png').read_bytes()).hexdigest()==prior['output']['G']['sha256']
scenarios={'G':'lv6-complete-g.png','H':'lv6-density-h.png','I':'lv6-density-i.png','J':'lv6-density-j.png','K':'lv6-density-k.png'}
g=Image.open(root/scenarios['G']).convert('RGB')
for key,name in scenarios.items():
 im=Image.open(root/name).convert('RGB')
 assert im.size==g.size==(1200,880),name
 assert (root/name).stat().st_size>200000,name
 if key!='G':
  assert ImageChops.difference(g,im).getbbox() is not None,key
 if key in ('H','I','J','K'):
  for rect in [(10,0,1190,50),(215,447,419,606),(808,496,1032,621)] if key!='J' else [(10,0,1190,50),(215,447,419,606)]:
   # No changes to unrelated title, bulletin, or photo slots (except J photo test).
   assert ImageChops.difference(g.crop(rect),im.crop(rect)).getbbox() is None,(key,rect)
print('IMAGE_INTEGRITY_PASS',flush=True)
view_names={'1':'lv1-baseline.png','A':'lv6-existing-a.png','B':'lv6-existing-b.png','C':'lv6-existing-c.png','D':'lv6-existing-d.png','E':'lv6-existing-e.png','F':'lv6-complete-f.png','G':'lv6-complete-g.png','H':'lv6-density-h.png','I':'lv6-density-i.png','J':'lv6-density-j.png','K':'lv6-density-k.png'}
reports=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for label,w,h,m in [('iphone390',390,844,True),('iphone430',430,932,True),('desktop1200',1200,880,False)]:
  ctx=b.new_context(viewport={'width':w,'height':h},is_mobile=m,has_touch=m,device_scale_factor=1)
  pg=ctx.new_page()
  errors=[]; pg.on('pageerror',lambda e:errors.append(str(e)))
  response=pg.goto((root/'index.html').as_uri(),wait_until='domcontentloaded')
  assert response.status==200,response.status
  assert pg.locator('#tabK').get_attribute('aria-selected')=='true'
  for key,name in view_names.items():
   pg.locator('#tab'+key).click()
   pg.wait_for_function('(filename)=>{let e=document.getElementById("visual");return e&&e.complete&&e.naturalWidth===1200&&e.src.endsWith(filename)}',arg=name,timeout=20000)
   assert pg.locator('#tab'+key).get_attribute('aria-selected')=='true',key
  pg.locator('#routes').click()
  assert pg.locator('#route-overlay').is_visible()
  pg.locator('#zoom').click()
  assert pg.locator('#stage').evaluate('(e)=>e.scrollWidth>e.clientWidth')
  assert pg.locator('body').evaluate('(e)=>e.scrollWidth<=window.innerWidth')
  assert not errors,errors
  if label=='iphone390':
   pg.locator('#routes').click()
   pg.screenshot(path=r'C:\Users\User\AppData\Local\Temp\a18_density_K_iphone390_qa.png',full_page=True)
  reports.append({'viewport':label,'tabs':12,'route':'PASS','zoom':'PASS','image_count':12,'horizontal_overflow':False,'javascript_errors':0})
  print('VIEWPORT_PASS',label,flush=True)
  ctx.close()
 b.close()
(root/'QA_density_results.json').write_text(json.dumps({'status':'PASS','checks':reports,'preserved_g_sha256':prior['output']['G']['sha256']},ensure_ascii=False,indent=2),encoding='utf8')
print('ALL_QA_PASS',flush=True)
