"""A18 current left light-oak sprite vs v05 plaster/v08. Game screenshot review and touch layout QA."""
from pathlib import Path
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parent
sprite=Image.open(root/'partition-left-oak-v09.png').convert('RGBA')
original=Image.open(root/'partition-left-plaster-v05.png').convert('RGBA')
assert sprite.size==original.size==(860,488)
# A18 v05's wooden pilasters, wainscot, border, transparent edge unchanged pixel-for-pixel.
import numpy as np
a,b=[np.asarray(x) for x in (sprite,original)]
delta=np.any(a!=b,axis=2)
mask=((np.indices(delta.shape)[1]>=69)&(np.indices(delta.shape)[1]<=724)&
      (np.indices(delta.shape)[0]>=59)&(np.indices(delta.shape)[0]<=333))
assert not (delta&~mask).any()
assert np.array_equal(a[:,:,3],b[:,:,3])
assert 180000<int(delta.sum())<=180400,int(delta.sum())
new=Image.open(root/'game_left_oak_v09.png').convert('RGB')
old=Image.open(root/'game_plaster_right_centered_v06.png').convert('RGB')
assert new.size==old.size==(1200,880)
assert ImageChops.difference(new,old).getbbox() is not None
assert new.crop((755,462,1064,688)).tobytes()==old.crop((755,462,1064,688)).tobytes()
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
 for width,height,mobile in [(1200,880,False),(390,844,True)]:
  page=browser.new_page(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  resp=page.goto('http://127.0.0.1:8338/entrance-partition-review-20261028/',wait_until='load',timeout=25000)
  assert resp.status==200
  assert page.title()=='A18｜カウンター奥・左壁の薄木材プレビュー'
  assert page.locator('#leftReview').is_visible()
  assert page.locator('#leftScreen').evaluate('(e)=>e.complete && e.naturalWidth')==1200
  assert page.locator('#leftScreen').get_attribute('src')=='game_left_oak_v09.png'
  for button,expected in [('leftOld','game_plaster_right_centered_v06.png'),
                          ('leftV08','game_left_wall_v08.png'),('leftNew','game_left_oak_v09.png')]:
   page.locator('#'+button).click()
   page.wait_for_function('(n) => document.querySelector("#leftScreen").getAttribute("src")===n',arg=expected)
   assert page.locator('#'+button).get_attribute('aria-pressed')=='true'
  page.locator('#tab-material').click()
  page.locator('#showLeft').click()
  page.wait_for_function('document.querySelector("#materialImg").complete && document.querySelector("#materialImg").naturalWidth===860')
  assert page.locator('#materialImg').get_attribute('src')=='partition-left-oak-v09.png'
  page.locator('#showRight').click()
  assert page.locator('#materialImg').get_attribute('src')=='partition-right-mirror-v03.png'
  page.locator('#tab-placement').click()
  assert page.locator('#placement .base').get_attribute('src')=='game_left_oak_v09_no_right.png'
  assert 'X=363, Y=243, 横幅=188, 高さ=133' in page.locator('#readout').inner_text()
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  assert not errors,errors
  page.locator('#tab-left').click()
  path=root/('qa_oak_v09_mobile.png' if mobile else 'qa_oak_v09_desktop.png')
  page.screenshot(path=str(path),full_page=True)
  results.append({'width':width,'height':height,'mobile':mobile,'result':'PASS','errors':errors})
  print('A18_OAK_V09_BROWSER_QA_PASS',width,height,'mobile',mobile)
  page.close()
 browser.close()
(root/'qa_left_oak_v09_report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
