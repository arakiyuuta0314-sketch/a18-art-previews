from pathlib import Path
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
import json,hashlib
r=Path(r'C:\Users\User\source\repos\a18-art-previews-publish\entrance-lv6-review-20261028')
mf=json.loads((r/'APPROVED_ENTRANCE_LV6_MANIFEST.json').read_text(encoding='utf8'))
approved=r/mf['approvedReferenceFile']
source=r/mf['previewSourceFile']
orig=r/mf['baselineLevel1File']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert mf['approvedVariant']=='U'
assert sha(approved)==sha(source)==mf['sha256']
assert approved.read_bytes()==source.read_bytes()
assert sha(orig)==mf['baselineLevel1Sha256']
assert Image.open(approved).size==(1200,880)
assert mf['runtimeIntegration']=='NOT_IMPLEMENTED'
print('APPROVAL_PROVENANCE_PASS',sha(approved),flush=True)
views=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for tag,w,h,mobile in [('iphone390',390,844,True),('iphone430',430,932,True),('desktop',1200,880,False)]:
  ctx=b.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
  page=ctx.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  res=page.goto((r/'index.html').as_uri(),wait_until='domcontentloaded')
  assert res.status==200
  assert page.locator('#tabU').get_attribute('aria-selected')=='true'
  assert '承認済み' in page.locator('#status').inner_text()
  page.wait_for_function('(f)=>{const i=document.querySelector("#visual");return i.complete&&i.naturalWidth===1200&&i.src.endsWith(f)}',arg=approved.name)
  for key,f in [('T','lv6-lush-t.png'),('U',approved.name),('V','lv6-standing-v.png')]:
   page.locator('#tab'+key).click()
   page.wait_for_function('(f)=>{const i=document.querySelector("#visual");return i.complete&&i.naturalWidth===1200&&i.src.endsWith(f)}',arg=f,timeout=14000)
  page.locator('#routes').click();assert page.locator('#route-overlay').is_visible()
  page.locator('#zoom').click();assert page.locator('#stage').evaluate('e=>e.scrollWidth>e.clientWidth')
  assert page.locator('body').evaluate('e=>e.scrollWidth<=innerWidth')
  assert not errors,errors
  views.append({'viewport':tag,'approved_image':'PASS','history_TUV':'PASS','route':'PASS','zoom':'PASS','jsErrors':0,'horizontalOverflow':False})
  print('APPROVED_WEB_QA_PASS',tag,flush=True)
  ctx.close()
 b.close()
(r/'QA_approved_lv6.json').write_text(json.dumps({'result':'PASS','image_SHA256':mf['sha256'],'views':views,'runtimeCodeUntouched':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('ALL_APPROVAL_QA_PASS',flush=True)
