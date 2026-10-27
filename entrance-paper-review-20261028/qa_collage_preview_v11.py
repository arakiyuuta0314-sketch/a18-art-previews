"""Live Chrome QA for organic 5-paper v11 vs old 3-paper v10."""
from pathlib import Path
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parent
files=['collage-v11.png','with-papers.png','collage-without.png','collage-photo-v11.png']
for f in files:assert Image.open(ROOT/f).size==(1200,880)
assert ImageChops.difference(Image.open(ROOT/files[0]),Image.open(ROOT/files[1])).getbbox()
for name in ['sage','notice','blue','ochre','rose']:
 im=Image.open(ROOT/('paper-'+name+'-v11.png'))
 assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for w,h,mobile in [(1200,880,False),(390,844,True)]:
  page=b.new_page(viewport={'width':w,'height':h},has_touch=mobile,is_mobile=mobile)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  r=page.goto('http://127.0.0.1:8338/entrance-paper-review-20261028/',wait_until='load',timeout=25000)
  assert r.status==200
  assert '重ね貼り' in page.title()
  for id,source in [('previous','with-papers.png'),('absent','collage-without.png'),('photo','collage-photo-v11.png'),('present','collage-v11.png')]:
   page.locator('#'+id).click()
   page.wait_for_function('(src)=>{const el=document.getElementById("game");return el.getAttribute("src")===src&&el.complete&&el.naturalWidth===1200}',arg=source,timeout=10000)
   assert page.locator('#'+id).get_attribute('aria-pressed')=='true'
  for name in ['sage','notice','blue','ochre','rose']:
   assert page.locator('img[src="paper-'+name+'-v11.png"]').evaluate('(e)=>e.complete&&e.naturalWidth>0')
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),w
  assert not errors,errors
  page.screenshot(path=str(ROOT/('qa_collage_v11_mobile.png' if mobile else 'qa_collage_v11_desktop.png')),full_page=True)
  results.append({'resolution':[w,h],'mobile':mobile,'pass':True,'errors':errors})
  print('A18_COLLAGE_REVIEW_PASS',w,h,mobile)
  page.close()
 b.close()
(ROOT/'qa_collage_preview_v11_report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
