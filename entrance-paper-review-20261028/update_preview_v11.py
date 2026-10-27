"""Migrate v10 reception preview to v11 without dropping v10 comparison."""
from pathlib import Path
p=Path(__file__).with_name('index.html')
s=p.read_text(encoding='utf8')
def one(a,b):
 global s
 assert s.count(a)==1,(a[:90],s.count(a))
 s=s.replace(a,b)
one('受付カウンター奥・紙の装飾プレビュー','受付カウンター奥・重ね貼りの紙プレビュー')
one('.tabs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));',
    '.tabs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));')
one('@media(max-width:610px){main{padding:14px 9px 34px}',
    '@media(max-width:610px){.tabs{grid-template-columns:repeat(2,minmax(0,1fr))}.grid{grid-template-columns:repeat(3,minmax(0,1fr))}main{padding:14px 9px 34px}')
one('v09の明るい木壁はそのまま。カウンターと左壁を15px下へ動かして、紙の装飾だけ追加した監修用プレビュー。',
    'v09の明るい木壁と家具の位置はそのまま。紙を重ねて傾け、5色・5枚の自然な貼り方に変更した監修用プレビュー。')
one('src="with-papers.png" width="1200" height="880" alt="実ゲームChrome画面。カウンター奥の木製仕切り壁にご案内と小さなメモ2枚を貼っている。カウンターと左壁は15ピクセル下げた配置"',
    'src="collage-v11.png" width="1200" height="880" alt="実ゲームChrome画面。カウンター裏の木壁に生成り・緑・水色・黄土・ピンクの5枚を少しずつ重ねて貼った受付"')
one('<button type="button" id="present" aria-pressed="true">紙あり</button>\n<button type="button" id="absent" aria-pressed="false">紙なし</button>\n<button type="button" id="photo" aria-pressed="false">右壁に作品あり</button>',
    '<button type="button" id="present" aria-pressed="true">重ね貼り（v11）</button>\n<button type="button" id="previous" aria-pressed="false">以前の横並び</button>\n<button type="button" id="absent" aria-pressed="false">紙なし</button>\n<button type="button" id="photo" aria-pressed="false">右壁に作品あり</button>')
one('ゲームを実際にChromeで動かして撮影した画面。紙3枚を表示しています。背景・キャラクター・右壁は変更していません。',
    'Chromeで実際にゲームを動かして撮影した画面。5枚を重ね、紙色・角度・留め具を変えています。背景・キャラクター・右壁は変更していません。')
start=s.index('<h2>独立素材：紙3枚</h2>')
end=s.index('<p class="foot">',start)
items=[
 ('paper-sage-v11.png','淡い緑','今日の予定を記した控えめなメモ'),
 ('paper-notice-v11.png','生成り','手前に重ねた展示案内'),
 ('paper-blue-v11.png','淡い水色','クリップで留めたスタッフ用紙'),
 ('paper-ochre-v11.png','黄土色','小さなMEMO用紙'),
 ('paper-rose-v11.png','薄いピンク','端に重ねたひとことメモ')
]
frag='<h2>独立素材：色違いの紙5枚</h2>\n<div class="grid">\n'
for file,name,info in items:
 frag+=f'<div class="item"><div class="picture checker"><img src="{file}" alt="{name}の回転した紙・透明PNG"></div><div class="desc"><strong>{name}</strong>{info}。<a href="{file}" target="_blank" rel="noopener">透過PNG</a></div></div>\n'
frag+='</div>\n'
s=s[:start]+frag+s[end:]
one('ゲーム内でも3枚の透明スプライトとして個別管理しています。',
    'ゲーム内でも5枚の透明スプライトとして個別管理しています。')
one("const buttons=['present','absent','photo'];","const buttons=['present','previous','absent','photo'];")
one(" present:['with-papers.png','紙3枚を表示した実Chromeゲーム画面です。カウンターと左壁はそれぞれ15px下げています。'],\n absent:['without-papers.png','紙を非表示にした実Chromeゲーム画面です。右壁や家具の配置は「紙あり」と同じです。'],\n photo:['right-photo-game.png','独立した紙装飾を表示したまま、右壁にテスト画像を登録して保存した実Chromeゲーム画面です。']",
    " present:['collage-v11.png','5枚を重ねて貼ったv11。生成り・緑・水色・黄土・ピンクの紙を角度をつけて配置しています。'],\n previous:['with-papers.png','比較用の前バージョン。生成り色の紙3枚が横並びだったv10の実ゲーム画面です。'],\n absent:['collage-without.png','新配置のまま装飾だけ非表示にした実Chrome画面です。'],\n photo:['collage-photo-v11.png','v11の重ね貼りを残したまま、右壁にテスト作品を登録した実ゲーム画面です。']")
p.write_text(s,encoding='utf8')
assert '重ね貼り（v11）' in p.read_text(encoding='utf8')
print('PAPER_PREVIEW_UPDATED_V11')
