"""Chrome QA for A18 plaster-left and right-wall photo feature preview."""
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parent
for name,size in [('partition-left-plaster-v05.png',(860,488)),
                  ('partition-right-mirror-v03.png',(860,488)),
                  ('game_plaster_right_registered_v05.png',(1200,880)),
                  ('game_plaster_right_empty_v05.png',(1200,880)),
                  ('game_plaster_without_right_v05.png',(1200,880))]:
    pic=Image.open(root/name)
    assert pic.size==size,(name,pic.size)
assert Image.open(root/'partition-left-plaster-v05.png').convert('RGBA').getpixel((350,150))[0]>210
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for width,height,mobile in [(1200,880,False),(390,844,True)]:
  page=b.new_page(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  r=page.goto('http://127.0.0.1:8338/entrance-partition-review-20261028/',wait_until='load',timeout=30000)
  assert r.status==200
  assert page.title()=='A18｜白漆喰の左壁と右壁の写真登録プレビュー'
  assert page.locator('#rightWall').evaluate('(e)=>e.complete&&e.naturalWidth')==860
  assert 'X=363, Y=243, 横幅=188, 高さ=133' in page.locator('#readout').inner_text()
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  page.locator('#w').fill('214')
  assert '横幅=214' in page.locator('#readout').inner_text()
  page.locator('#reset').click()
  assert '横幅=188' in page.locator('#readout').inner_text()
  box=page.locator('#rightWall').bounding_box()
  assert box and box['width']>30,box
  # All functions used in the app preview are functional.
  page.locator('#tab-photo').click()
  assert page.locator('#photoPreview').is_visible()
  assert page.locator('#registeredScreen').evaluate('(e)=>e.complete&&e.naturalWidth')==1200
  page.locator('#photoAbsent').click()
  assert page.locator('#registeredScreen').get_attribute('src')=='game_plaster_right_empty_v05.png'
  page.locator('#photoPresent').click()
  assert page.locator('#registeredScreen').get_attribute('src')=='game_plaster_right_registered_v05.png'
  page.screenshot(path=str(root/('qa_v05_mobile.png' if mobile else 'qa_v05_desktop.png')),full_page=True)
  page.locator('#tab-material').click()
  page.locator('#showLeft').click()
  page.wait_for_function('document.querySelector("#materialImg").complete && document.querySelector("#materialImg").naturalWidth===860')
  assert page.locator('#materialImg').get_attribute('src')=='partition-left-plaster-v05.png'
  page.locator('#showRight').click()
  page.wait_for_function('document.querySelector("#materialImg").complete && document.querySelector("#materialImg").naturalWidth===860')
  assert page.locator('#materialImg').get_attribute('src')=='partition-right-mirror-v03.png'
  assert not errors,errors
  results.append({'device':'iPhone width390' if mobile else 'desktop width1200','status':'PASS','page_errors':errors})
  print('PLASTER_AND_PHOTO_PREVIEW_PASS',width,height,'mobile',mobile)
  page.close()
 b.close()
(root/'qa_plaster_photo_v05_report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
