"""A18 independent partition material preview: local Chrome QA, phone QA and alpha check."""
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent
png=Image.open(root/'partition.png').convert('RGBA')
assert png.size==(768,528),png.size
lo,hi=png.getchannel('A').getextrema()
assert lo==0 and hi==255, (lo,hi)
a=Image.open(root/'with-partition.png').convert('RGB')
b=Image.open(root/'counter-only.png').convert('RGB')
assert a.size==b.size==(1200,880)
assert ImageChops.difference(a,b).getbbox() is not None
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
    for width,height in [(1200,880),(390,844)]:
        pg=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        errors=[]
        pg.on('pageerror',lambda x:errors.append(str(x)))
        r=pg.goto('http://127.0.0.1:8338/entrance-partition-review-20261028/',wait_until='load',timeout=20000)
        assert r.status==200,r.status
        assert pg.title()=='A18｜仕切り壁・独立素材確認'
        assert pg.locator('#screen').evaluate('(x)=>x.complete && x.naturalWidth===1200')
        pg.locator('#without').click()
        assert pg.locator('#screen').get_attribute('src')=='counter-only.png'
        pg.locator('#with').click()
        assert pg.locator('#screen').get_attribute('src')=='with-partition.png'
        pg.locator('#tab-asset').click()
        assert pg.locator('#asset').is_visible()
        assert pg.locator('#asset img').evaluate('(x)=>x.complete && x.naturalWidth===768')
        assert pg.locator('a[href="partition.png"]').count()==1
        assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),width
        assert not errors, errors
        pg.screenshot(path=str(root/('qa_asset_mobile.png' if width==390 else 'qa_asset_desktop.png')),full_page=True)
        pg.locator('#tab-game').click()
        assert pg.locator('#game').is_visible()
        pg.screenshot(path=str(root/('qa_game_mobile.png' if width==390 else 'qa_game_desktop.png')),full_page=True)
        print('PARTITION_PREVIEW_PASS',width,height)
        pg.close()
    browser.close()
