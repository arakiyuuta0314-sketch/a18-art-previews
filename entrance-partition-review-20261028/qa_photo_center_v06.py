"""Review page: centered photo versus previous and empty, phone/desktop."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageChops
import json
root=Path(__file__).resolve().parent
files=['game_plaster_right_centered_v06.png','game_plaster_right_registered_v05.png','game_plaster_right_empty_v05.png']
images=[Image.open(root/n).convert('RGB') for n in files]
assert all(im.size==(1200,880) for im in images)
assert ImageChops.difference(images[0],images[1]).getbbox() is not None
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for width,height,mobile in [(1200,880,False),(390,844,True)]:
  page=browser.new_page(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  r=page.goto('http://127.0.0.1:8338/entrance-partition-review-20261028/',wait_until='load',timeout=30000)
  assert r.status==200,r.status
  page.locator('#tab-photo').click()
  assert page.locator('#photoPreview').is_visible()
  assert page.locator('#registeredScreen').get_attribute('src')==files[0]
  assert page.locator('#registeredScreen').evaluate('(el)=>el.complete&&el.naturalWidth')==1200
  page.locator('#photoBefore').click()
  assert page.locator('#registeredScreen').get_attribute('src')==files[1]
  page.locator('#photoAbsent').click()
  assert page.locator('#registeredScreen').get_attribute('src')==files[2]
  page.locator('#photoPresent').click()
  assert page.locator('#registeredScreen').get_attribute('src')==files[0]
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  assert not errors,errors
  name='qa_center_v06_mobile.png' if mobile else 'qa_center_v06_desktop.png'
  page.screenshot(path=str(root/name),full_page=True)
  results.append({'viewport':[width,height],'mobile':mobile,'result':'PASS','errors':errors})
  print('PHOTO_CENTER_PREVIEW_PASS',width,height)
  page.close()
 browser.close()
(root/'qa_photo_center_v06_report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
