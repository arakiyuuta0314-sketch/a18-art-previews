"""Extract the foreground actually rendered by A18's game code; preserve fixed counter and butler over movable screen."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
from io import BytesIO
import base64,json
root=Path(__file__).resolve().parent
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1200,'height':880},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    r=page.goto('http://127.0.0.1:8232/layout-test/index.html',wait_until='domcontentloaded',timeout=30000)
    assert r.status==200
    page.locator('#a18OpeningStart').click()
    page.locator('#a18OpeningSkip').click()
    page.locator('#a18PlayerName').fill('確認用')
    page.locator('#confirmName').click()
    page.wait_for_function('window.__A18_SCENE_STUDY__ && window.__A18_SCENE_STUDY__.ready()',timeout=20000)
    page.wait_for_timeout(700)
    data=page.evaluate("""() => {
      const world=document.querySelector('#world');
      const rect=world.getBoundingClientRect();
      const info=window.__A18_SCENE_STUDY__.state();
      const canvas=document.createElement('canvas');canvas.width=1200;canvas.height=880;
      const context=canvas.getContext('2d');
      // The canvas is scaled into the CSS viewport; use measured bounds, not hand-estimated offsets.
      const sx=rect.width/world.width,sy=rect.height/world.height;
      const screenScale=world.width/info.viewport.logicalW;
      context.setTransform(sx*screenScale,0,0,sy*screenScale,rect.left,rect.top);
      window.A18Art.npc(context,'butler',139,366);
      window.A18Entrance.counter(context);
      context.setTransform(1,0,0,1,0,0);
      return {png:canvas.toDataURL('image/png'),rect:{x:rect.left,y:rect.top,w:rect.width,h:rect.height},
        info:info.viewport,canvas:{w:world.width,h:world.height},
        positions:{counter:{x:-10,y:308,w:233,h:107},butler:{x:139,footY:366}}};
    }""")
    img=Image.open(BytesIO(base64.b64decode(data.pop('png').split(',',1)[1]))).convert('RGBA')
    assert img.size==(1200,880)
    assert img.getchannel('A').getbbox() is not None
    output=root/'foreground-counter-butler.png'
    img.save(output,optimize=True)
    print('A18_FOREGROUND_OVERLAY',json.dumps(data,ensure_ascii=False),'bounds',img.getchannel('A').getbbox(),'bytes',output.stat().st_size,'errors',errors)
    assert not errors
    (root/'overlay_geometry.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf8')
    browser.close()
