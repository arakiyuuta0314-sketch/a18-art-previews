"""Chrome QA for independent mirrored partition and interactive right-wall placement."""
from pathlib import Path
from PIL import Image,ImageOps
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parent
left=Image.open(ROOT/'partition-left-v03.png').convert('RGBA')
right=Image.open(ROOT/'partition-right-mirror-v03.png').convert('RGBA')
assert left.size==right.size==(860,488)
assert ImageOps.mirror(left).tobytes()==right.tobytes()
assert left.getchannel('A').getextrema()==(0,255)
game=Image.open(ROOT/'game_left_fixed_counter_y318.png').convert('RGB')
assert game.size==(1200,880)
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 for width,height,mobile in [(1200,880,False),(390,844,True)]:
  page=browser.new_page(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  r=page.goto('http://127.0.0.1:8338/entrance-partition-review-20261028/',wait_until='load',timeout=25000)
  assert r.status==200,r.status
  assert page.title()=='A18｜左右仕切り壁・配置調整プレビュー'
  for sel,n in [('.base',1200),('#rightWall',860)]:
   assert page.locator(sel).evaluate('(e)=>e.complete && e.naturalWidth')==n,sel
  assert 'X=337, Y=200, 横幅=215, 高さ=122' in page.locator('#readout').inner_text()
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  screenshot=ROOT/('qa_v03_mobile.png' if mobile else 'qa_v03_desktop.png')
  page.screenshot(path=str(screenshot),full_page=True)
  page.locator('#w').fill('235')
  page.locator('#h').fill('118')
  page.locator('#x').fill('318')
  assert 'X=318, Y=200, 横幅=235, 高さ=118' in page.locator('#readout').inner_text()
  page.locator('#hide').click()
  assert page.locator('#rightWall').is_hidden()
  page.locator('#show').click()
  assert page.locator('#rightWall').is_visible()
  page.locator('#reset').click()
  assert 'X=337, Y=200, 横幅=215, 高さ=122' in page.locator('#readout').inner_text()
  item=page.locator('#rightWall')
  item.scroll_into_view_if_needed()
  bounds=item.bounding_box()
  x=bounds['x']+bounds['width']*.3
  y=bounds['y']+bounds['height']*.3
  if mobile:
   cdp=page.context.new_cdp_session(page)
   cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
   cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x-20,'y':y+16}]})
   cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
   page.wait_for_timeout(120)
  else:
   page.mouse.move(x,y)
   page.mouse.down()
   page.mouse.move(x-35,y+16,steps=7)
   page.mouse.up()
  assert page.locator('#x').input_value()!='337',page.locator('#readout').inner_text()
  page.locator('#tab-material').click()
  assert page.locator('#material').is_visible()
  page.locator('#showLeft').click()
  page.wait_for_function('document.querySelector("#materialImg").complete && document.querySelector("#materialImg").naturalWidth === 860')
  assert page.locator('#materialImg').evaluate('(e)=>e.complete && e.naturalWidth')==860
  assert page.locator('#materialImg').get_attribute('src')=='partition-left-v03.png'
  page.locator('#showRight').click()
  assert page.locator('#materialImg').get_attribute('src')=='partition-right-mirror-v03.png'
  assert not errors,errors
  results.append({'viewport':[width,height],'mobile':mobile,'passed':True,'errors':errors})
  print('LEFT_FIXED_RIGHT_MOVABLE_PASS',width,height,'mobile',mobile)
  page.close()
 browser.close()
(ROOT/'qa_both_partitions_v03_report.json').write_text(json.dumps(results,indent=2),encoding='utf8')
