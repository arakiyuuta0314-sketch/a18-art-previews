"""Local regression of A18 aesthetic comparison K/L/M/M+; no changes to game."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
from playwright.sync_api import sync_playwright
import json,hashlib
D=Path(__file__).parent
man=json.loads((D/'lm-preview-manifest.json').read_text(encoding='utf-8'))
paths={'K':'lv6-density-k.png','L':'lv6-l-bench.png','M':'lv6-m-bench-light.png','N':'lv6-mplus-bench-light.png'}
for key,rel in paths.items():
 p=D/rel
 assert p.exists() and p.stat().st_size>200000,(key,p)
 img=Image.open(p).convert('RGB')
 assert img.size==(1200,880),(key,img.size)
 if key!='K':
  record=man['output'][{'L':'L','M':'M','N':'M_plus'}[key]]
  assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256'],key
K=Image.open(D/paths['K']).convert('RGB'); L=Image.open(D/paths['L']).convert('RGB')
M=Image.open(D/paths['M']).convert('RGB'); N=Image.open(D/paths['N']).convert('RGB')
# No furniture changes elsewhere in K->L; only within the lower-right bench/shadow region.
zone=(756,724,986,844)
other=Image.new('RGB',(1200,880),(0,0,0))
from PIL import ImageDraw
mask=Image.new('L',(1200,880),255)
ImageDraw.Draw(mask).rectangle(zone,fill=0)
diff=ImageChops.difference(K,L)
assert diff.getbbox()
assert diff.getchannel('R').getextrema()[1]>0
assert ImageChops.difference(K,L).getchannel('R').getbbox() is not None
# RGB differences outside the furniture bbox would indicate unintended updates
for a,b in [(K,L)]:
 delta=ImageChops.difference(a,b).convert('L')
 delta=ImageChops.multiply(delta,mask)
 assert delta.getbbox() is None,('K->L changed unrelated image pixels',delta.getbbox())
# keep title and frame center / photo interiors protected from illumination effects
for name,img in [('L',L),('M',M),('N',N)]:
 for box in [(0,0,1200,53),(210,167,450,299),(785,167,986,297),(819,500,1028,603)]:
  assert ImageChops.difference(K.crop(box),img.crop(box)).getbbox() is None,(name,box)
# quantify increasing illumination on the architectural back wall and the floor
def avg(im,box):
 return ImageStat.Stat(im.crop(box)).mean[0]
for rect in [(512,120,549,327),(767,409,1057,469)]:
 assert avg(M,rect)>avg(L,rect),(rect,avg(M,rect),avg(L,rect))
 assert avg(N,rect)>avg(M,rect),(rect,avg(N,rect),avg(M,rect))
print('IMAGE_QA_PASS verified original K, source bench isolated, lighting strength increases',flush=True)
report=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for tag,w,h,mobile in [('iphone390',390,844,True),('iphone430',430,932,True),('desktop',1200,880,False)]:
  ctx=b.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
  page=ctx.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  r=page.goto((D/'index.html').as_uri(),wait_until='domcontentloaded',timeout=30000)
  assert r.status==200
  assert page.locator('#tabM').get_attribute('aria-selected')=='true'
  assert page.locator('details.history').get_attribute('open') is None
  for key,path in paths.items():
   page.locator('#tab'+key).click()
   page.wait_for_function('(s)=>{const i=document.getElementById("visual");return i&&i.complete&&i.naturalWidth===1200&&i.src.endsWith(s)}',arg=path,timeout=16000)
   assert page.locator('#tab'+key).get_attribute('aria-selected')=='true'
  page.locator('#tabM').click()
  page.locator('#routes').click()
  assert page.locator('#route-overlay').is_visible()
  page.locator('#routes').click()
  page.locator('#zoom').click()
  assert page.locator('#stage').evaluate('e=>e.scrollWidth>e.clientWidth')
  page.locator('#zoom').click()
  assert page.locator('body').evaluate('e=>e.scrollWidth<=window.innerWidth')
  # Historical cases remain accessible in a collapsible section.
  page.locator('details.history summary').click()
  for key in ['1','A','B','C','D','E','F','G','H','I','J']:
   page.locator('#tab'+key).click()
   assert page.locator('#tab'+key).get_attribute('aria-selected')=='true'
  assert not errors,errors
  page.locator('#tabM').click()
  if tag=='iphone390':
   page.locator('details.history summary').click()
   page.screenshot(path=r'C:\Users\User\AppData\Local\Temp\A18_lm_iphone390_QA_20261028.png',full_page=True)
  report.append({'viewport':tag,'screen':[w,h],'primary_tabs':4,'old_tabs':11,'zoom':'PASS','routes':'PASS','no_horizontal_overflow':True,'js_errors':0})
  print('BROWSER_QA_PASS',tag,flush=True)
  ctx.close()
 b.close()
(D/'QA_lm_results.json').write_text(json.dumps({'result':'PASS','screens':report,'preserved_k_sha256':hashlib.sha256((D/paths['K']).read_bytes()).hexdigest()},ensure_ascii=False,indent=2),encoding='utf8')
print('ALL_LM_QA_PASS',flush=True)
