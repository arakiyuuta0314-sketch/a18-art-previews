"""A18 architecture-left art review: public preview local UI and exact independent assets."""
from pathlib import Path
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parent
assert Image.open(root/'partition-left-wall-v08.png').size==(860,488)
assert Image.open(root/'partition-left-wall-v08.png').mode=='RGBA'
new=Image.open(root/'game_left_wall_v08.png').convert('RGB')
old=Image.open(root/'game_plaster_right_centered_v06.png').convert('RGB')
assert new.size==old.size==(1200,880)
assert ImageChops.difference(new,old).getbbox()
# Areas with right wall must remain unaffected by the left-wall change.
assert new.crop((760,455,1066,695)).tobytes()==old.crop((760,455,1066,695)).tobytes()
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 for width,height,mobile in [(1200,880,False),(390,844,True)]:
  pg=b.new_page(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile)
  errs=[]
  pg.on('pageerror',lambda e:errs.append(str(e)))
  resp=pg.goto('http://127.0.0.1:8338/entrance-partition-review-20261028/',wait_until='load',timeout=30000)
  assert resp.status==200
  assert pg.title()=='A18｜カウンター奥・左漆喰壁の実ゲームプレビュー'
  assert pg.locator('#leftReview').is_visible()
  assert pg.locator('#leftScreen').evaluate('(e)=>e.complete&&e.naturalWidth')==1200
  pg.locator('#leftOld').click()
  assert pg.locator('#leftScreen').get_attribute('src')=='game_plaster_right_centered_v06.png'
  pg.locator('#leftNew').click()
  assert pg.locator('#leftScreen').get_attribute('src')=='game_left_wall_v08.png'
  pg.locator('#tab-material').click()
  pg.locator('#showLeft').click()
  pg.wait_for_function('document.querySelector("#materialImg").complete && document.querySelector("#materialImg").naturalWidth===860')
  assert pg.locator('#materialImg').get_attribute('src')=='partition-left-wall-v08.png'
  pg.locator('#showRight').click()
  pg.wait_for_function('document.querySelector("#materialImg").complete && document.querySelector("#materialImg").naturalWidth===860')
  assert pg.locator('#materialImg').get_attribute('src')=='partition-right-mirror-v03.png'
  pg.locator('#tab-photo').click()
  assert pg.locator('#photoPreview').is_visible()
  pg.locator('#photoBefore').click()
  pg.locator('#photoPresent').click()
  assert pg.locator('#registeredScreen').get_attribute('src')=='game_plaster_right_centered_v06.png'
  pg.locator('#tab-placement').click()
  assert pg.locator('#placement').is_visible()
  assert 'X=363, Y=243, 横幅=188, 高さ=133' in pg.locator('#readout').inner_text()
  assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
  assert not errs,errs
  pg.locator('#tab-left').click()
  pg.screenshot(path=str(root/('qa_left_wall_v08_mobile.png' if mobile else 'qa_left_wall_v08_desktop.png')),full_page=True)
  results.append({'width':width,'height':height,'mobile':mobile,'errors':errs,'result':'PASS'})
  print('ARCHITECTURAL_LEFT_V08_PREVIEW_PASS',width,height,'mobile',mobile)
  pg.close()
 b.close()
(root/'qa_left_wall_v08_report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
