"""QA for A18 draggable partition preview. Tests real Chrome and iPhone-sized layout."""
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
import json
root=Path(__file__).resolve().parent
png=Image.open(root/'partition.png').convert('RGBA')
assert png.size==(768,528)
wide=Image.open(root/'partition-wide-v02.png').convert('RGBA')
assert wide.size==(928,496)
assert wide.getchannel('A').getextrema()==(0,255)
assert png.getchannel('A').getextrema()==(0,255)
layer=Image.open(root/'foreground-counter-butler.png').convert('RGBA')
assert layer.size==(1200,880)
assert layer.getchannel('A').getbbox() is not None
base=Image.open(root/'counter-only.png').convert('RGB')
assert base.size==(1200,880)
results=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
    for width,height,mobile in [(1200,880,False),(390,844,True)]:
        page=b.new_page(viewport={'width':width,'height':height},
            is_mobile=mobile,has_touch=mobile,device_scale_factor=2 if mobile else 1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        r=page.goto('http://127.0.0.1:8338/entrance-partition-review-20261028/',
                    wait_until='load',timeout=20000)
        assert r.status==200,r.status
        assert page.title()=='A18｜仕切り壁の配置調整プレビュー'
        for selector,w in [('.base',1200),('#partition',928),('.foreground',1200)]:
            assert page.locator(selector).evaluate('(x)=>x.complete && x.naturalWidth')==w,selector
        assert 'X=12, Y=231, 横幅=232, 高さ=124' in page.locator('#readout').inner_text()
        assert page.locator('#tab-adjust').get_attribute('aria-selected')=='true'
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
        box=page.locator('#partition').bounding_box()
        assert box and box['width']>0
        # Initial screen image differs from the source screenshot due to the movable wall.
        page.screenshot(path=str(root/('qa_v02_mobile.png' if mobile else 'qa_v02_desktop.png')),full_page=True)
        for control,value in [('x','52'),('y','239'),('w','255'),('h','118')]:
            page.locator('#'+control).fill(value)
        assert 'X=52, Y=239, 横幅=255, 高さ=118' in page.locator('#readout').inner_text()
        page.locator('#without').click()
        assert page.locator('#partition').evaluate('(x)=>getComputedStyle(x).display')=='none'
        page.locator('#with').click()
        assert page.locator('#partition').is_visible()
        page.locator('#reset').click()
        assert 'X=12, Y=231, 横幅=232, 高さ=124' in page.locator('#readout').inner_text()
        # Drag on visible wall region, separate from fixed foreground sprites.
        item=page.locator('#partition')
        item.scroll_into_view_if_needed()
        item_box=item.bounding_box()
        x,y=item_box['x']+item_box['width']*.50,item_box['y']+item_box['height']*.2
        if mobile:
            cdp=page.context.new_cdp_session(page)
            cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
            cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+24,'y':y+15}]})
            cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
            page.wait_for_timeout(120)
        else:
            page.mouse.move(x,y)
            page.mouse.down()
            page.mouse.move(x+30,y+18,steps=6)
            page.mouse.up()
        assert page.locator('#x').input_value()!='12',page.locator('#readout').inner_text()
        page.locator('#reset').click()
        page.locator('#tab-asset').click()
        assert page.locator('#asset-panel').is_visible()
        assert page.locator('a[href="partition-wide-v02.png"]').count()==1
        page.locator('#tab-adjust').click()
        assert page.locator('#adjust-panel').is_visible()
        assert not errors,errors
        results.append({'width':width,'height':height,'mobile':mobile,'result':'PASS'})
        print('PARTITION_INTERACTIVE_PREVIEW_PASS',width,height,'mobile',mobile)
        page.close()
    b.close()
(root/'qa_v02_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
