"""Browser QA: actual rendered HTML in mobile Chromium emulation, not physical Safari."""
from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright
D=Path(__file__).resolve().parent
url=sys.argv[1] if len(sys.argv)>1 else (D/'index.html').resolve().as_uri()
public=bool(len(sys.argv)>1)
report={'url':url,'engine':'Chromium','physical_iPhone_Safari':'NOT_TESTED','viewports':{}}
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
    for width,height in [(390,844),(375,812),(1440,900)]:
        context=browser.new_context(viewport={'width':width,'height':height},
             device_scale_factor=2 if width<500 else 1,is_mobile=width<500,has_touch=width<500)
        page=context.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append('JS '+str(e)))
        page.on('console',lambda m:errors.append('CONSOLE '+m.text) if m.type=='error' else None)
        response=page.goto(url,wait_until='domcontentloaded',timeout=45000)
        if public: assert response.status==200,response.status
        assert page.locator('article.panel').count()==6
        assert page.locator('article.approved').count()==2
        for i in range(6):
            img=page.locator('article.panel img').nth(i)
            img.scroll_into_view_if_needed()
            img.evaluate('(im)=>im.decode()')
            natural=img.evaluate('(im)=>[im.naturalWidth,im.naturalHeight,im.complete]')
            assert natural==[1200,880,True],(i,natural)
        overflow=page.evaluate('({scroll:document.documentElement.scrollWidth,inner:innerWidth})')
        assert overflow['scroll']<=overflow['inner']+2,overflow
        if width<500:
            page.locator('#two').check()
            assert page.locator('body.two').count()==1
            page.locator('#two').uncheck()
            assert page.locator('body.two').count()==0
        assert errors==[],errors
        name_prefix='qa-public' if public else 'qa-local'
        page.screenshot(path=str(D/f'{name_prefix}-{width}.png'),full_page=True)
        report['viewports'][f'{width}x{height}']={'images_loaded':6,'errors':errors,'overflow':overflow,'two_column_toggled':width<500}
        context.close()
    browser.close()
name='qa-public-browser-results.json' if public else 'qa-local-browser-results.json'
(D/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('BROWSER_QA_PASS',url,report['viewports'],flush=True)
