"""Chrome PC+iPhone screen QA for A18 reception paper assets review."""
from pathlib import Path
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parent
sizes={'with-papers.png':(1200,880),'without-papers.png':(1200,880),
'right-photo-game.png':(1200,880),'notice.png':(268,204),'memo.png':(152,132),'small-note.png':(124,116)}
for name,size in sizes.items():
 img=Image.open(root/name)
 assert img.size==size,(name,img.size)
 if name in ('notice.png','memo.png','small-note.png'):
  assert img.mode=='RGBA' and img.getchannel('A').getextrema()==(0,255),name
assert ImageChops.difference(Image.open(root/'with-papers.png'),Image.open(root/'without-papers.png')).getbbox()
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 for w,h,mob in ((1200,880,False),(390,844,True)):
  page=browser.new_page(viewport={'width':w,'height':h},is_mobile=mob,has_touch=mob)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  r=page.goto('http://127.0.0.1:8338/entrance-paper-review-20261028/',wait_until='load',timeout=25000)
  assert r.status==200,r.status
  assert page.title()=='A18｜受付カウンター奥・紙の装飾プレビュー'
  for k in sizes:
   assert page.locator('img[src="'+k+'"]').count() or k in ('without-papers.png','right-photo-game.png')
  for button,filename in [('absent','without-papers.png'),('photo','right-photo-game.png'),('present','with-papers.png')]:
   page.locator('#'+button).click()
   page.wait_for_function('(name) => {const i=document.querySelector("#game");return i.getAttribute("src")===name&&i.complete&&i.naturalWidth===1200}',arg=filename)
   assert page.locator('#'+button).get_attribute('aria-pressed')=='true'
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),w
  assert not errors,errors
  page.screenshot(path=str(root/('qa_paper_preview_mobile.png' if mob else 'qa_paper_preview_desktop.png')),full_page=True)
  results.append({'viewport':[w,h],'mobile':mob,'errors':errors,'pass':True})
  print('A18_PAPER_PREVIEW_PASS',w,h,mob)
  page.close()
 browser.close()
(root/'qa_paper_preview_v10_report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
