"""Smoke QA for A18 temporary counter art preview, including iPhone width."""
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
URL='http://127.0.0.1:8338/entrance-counter-review-20261028/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
    for width,height in [(1200,880),(390,844)]:
        pg=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        response=pg.goto(URL,wait_until='load',timeout=20000)
        assert response.status==200
        assert pg.title()=='A18｜受付カウンター 実ゲーム画面プレビュー'
        assert pg.locator('#actual').evaluate('(el)=>el.complete && el.naturalWidth===1200')
        pg.locator('#show-before').click()
        assert pg.locator('#actual').get_attribute('src')=='before-game.png'
        pg.locator('#show-current').click()
        assert pg.locator('#actual').get_attribute('src')=='actual-game.png'
        pg.locator('#tab-adjust').click()
        assert pg.locator('#adjust-panel').is_visible()
        assert pg.locator('#counter').evaluate('(el)=>el.complete && el.naturalWidth===936')
        assert 'X=34' in pg.locator('#readout').inner_text()
        pg.locator('#w').fill('225')
        assert '横幅=225' in pg.locator('#readout').inner_text()
        pg.locator('#reset').click()
        assert '横幅=200' in pg.locator('#readout').inner_text()
        assert pg.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errs,errs
        pg.locator('#tab-game').click()
        pg.screenshot(path=str(ROOT/('qa_local_'+str(width)+'.png')),full_page=True)
        print('PASS',width,height,'assets',pg.evaluate('performance.getEntriesByType("resource").filter(x=>x.name.includes(".png") || x.name.includes(".webp")).length'))
        pg.close()
    b.close()
