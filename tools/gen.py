# index.html, README.md, subjects/*.md 생성 스크립트 (tools 폴더에서 python3 gen.py)
# PRETENDARD_WOFF2=<PretendardVariable.woff2 경로>를 주면 글꼴을 넣은 미리보기용 matrix.html도 만든다.
import sys, html, json, os, base64, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import PROCESSES, KNOWLEDGE, CELLS, PATHS
from subjects import SUBJECTS
E = html.escape
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

CSS = """
<title>블룸 탐구활동 매트릭스</title>
<meta name="claude:viewport-fit-sides" content="cover">
%%FONT%%
<style>
/* 레이아웃: 머리말 → 과목 탭 → 4×6 매트릭스(가로 스크롤) → 과목 성취기준 목록 → 탐구 경로 → 활용 안내 */
:root{
  --bg:#f6f7f9; --surface:#ffffff; --fg:#1d2430; --muted:#5b6575; --line:#d9dee6;
  --accent:#2f5d8a; --accent-ink:#ffffff; --chip:#e7eef6;
  --l1:#eef3f8; --l2:#e3ecf5; --l3:#d6e4f1; --l4:#c8dbec; --l5:#b9d1e8; --l6:#a9c6e3;
  --hl:#f2c14e;
  --display:"Pretendard Variable", Pretendard, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
  --body:"Pretendard Variable", Pretendard, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#12161c; --surface:#1a2029; --fg:#e4e8ee; --muted:#9aa4b2; --line:#2c3542; --accent:#8fb8e0; --accent-ink:#0f1620; --chip:#223042;
  --l1:#18212c; --l2:#1b2632; --l3:#1e2b39; --l4:#213041; --l5:#243649; --l6:#283c52; --hl:#d9a93a; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#12161c; --surface:#1a2029; --fg:#e4e8ee; --muted:#9aa4b2; --line:#2c3542; --accent:#8fb8e0; --accent-ink:#0f1620; --chip:#223042;
  --l1:#18212c; --l2:#1b2632; --l3:#1e2b39; --l4:#213041; --l5:#243649; --l6:#283c52; --hl:#d9a93a; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.6;word-break:keep-all;overflow-wrap:break-word}
.wrap{max-width:1280px;margin:0 auto;padding-block:40px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:36px}
.wrap>*{min-width:0}
header{display:grid;gap:10px;max-width:72ch}
.eyebrow{font-size:12px;letter-spacing:.08em;color:var(--accent);font-weight:600}
h1{font-family:var(--display);font-weight:800;letter-spacing:-.02em;font-size:clamp(26px,4vw,38px);line-height:1.25;margin:0;text-wrap:balance}
h2{font-family:var(--display);font-weight:700;letter-spacing:-.01em;font-size:22px;margin:0 0 4px;text-wrap:balance}
p{margin:0}
.lead{color:var(--muted)}
.tabs{display:flex;flex-wrap:wrap;gap:8px}
.tab{font:inherit;font-size:14px;font-weight:600;border:1px solid var(--line);background:var(--surface);color:var(--fg);border-radius:999px;padding:6px 14px;cursor:pointer}
.tab small{font-weight:400;color:var(--muted);margin-left:4px}
.tab[aria-selected="true"]{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.tab[aria-selected="true"] small{color:inherit;opacity:.8}
.tab:focus-visible,.std-cell:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.subject-note{font-size:13px;color:var(--muted);margin-top:10px}
.scroller{overflow-x:auto;border:1px solid var(--line);border-radius:6px;background:var(--surface)}
table.mx{border-collapse:collapse;width:100%;min-width:1080px;table-layout:fixed}
.mx th,.mx td{border:1px solid var(--line);vertical-align:top;text-align:left;padding:12px}
.mx thead th{background:var(--surface);font-weight:600}
.mx thead th .ko{display:block;font-family:var(--display);font-size:18px;font-weight:700}
.en{font-size:11px;letter-spacing:.06em;color:var(--muted);text-transform:uppercase}
.mx thead th .def{display:block;font-weight:400;font-size:12px;color:var(--muted);margin-top:4px;line-height:1.45}
.mx thead th .vb{display:block;font-weight:500;font-size:12px;color:var(--accent);margin-top:6px}
.corner{width:150px;font-size:12px;color:var(--muted);font-weight:500}
.dim{background:var(--surface)}
.dim .ko{display:block;font-family:var(--display);font-size:17px;font-weight:700}
.dim .def{display:block;font-size:12px;color:var(--muted);margin-top:4px;line-height:1.45}
.mx td{font-size:13.5px}
.mx td.p1{background:var(--l1)} .mx td.p2{background:var(--l2)} .mx td.p3{background:var(--l3)}
.mx td.p4{background:var(--l4)} .mx td.p5{background:var(--l5)} .mx td.p6{background:var(--l6)}
.code{font-size:11px;font-weight:700;color:var(--accent);font-variant-numeric:tabular-nums;letter-spacing:.04em}
.mx ul{margin:4px 0 8px;padding-left:16px;display:grid;gap:4px}
.ref{display:inline-block;font-size:11px;font-variant-numeric:tabular-nums;color:var(--accent);background:var(--chip);border-radius:4px;padding:0 5px;margin-left:4px;white-space:nowrap}
.ref[data-code]{cursor:help}
.ref:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.stds .ref{margin:0 4px 0 0}
.stds .ref.main{font-weight:700;box-shadow:inset 0 0 0 1px var(--accent)}
.tip{position:fixed;z-index:20;max-width:min(360px,calc(100vw - 32px));background:var(--fg);color:var(--bg);font-size:13px;line-height:1.5;padding:8px 10px;border-radius:6px;box-shadow:0 4px 16px rgba(0,0,0,.18);pointer-events:none}
.tip b{display:block;font-size:11px;letter-spacing:.03em;opacity:.75;margin-bottom:2px}
.out,.stds{font-size:12px;color:var(--muted);border-top:1px dashed var(--line);padding-top:6px;margin-top:6px}
.out b,.stds b{font-weight:600;color:var(--fg)}
.mx td.on{outline:3px solid var(--hl);outline-offset:-3px}
.axis{font-size:12px;color:var(--muted);margin-top:8px}
table.st{border-collapse:collapse;width:100%;min-width:640px;background:var(--surface)}
.st th,.st td{border-bottom:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top;font-size:14px}
.st th{font-size:12px;color:var(--muted);font-weight:600}
.st td.c{white-space:nowrap;font-variant-numeric:tabular-nums;font-weight:600;color:var(--accent);font-size:13px}
.st td.k{white-space:nowrap}
.std-cell{font:inherit;font-size:12px;font-weight:600;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:4px;padding:1px 7px;margin:0 4px 4px 0;cursor:pointer}
.std-cell.main{border-color:var(--accent)}
.std-cell span{font-weight:400;color:var(--muted);margin-left:3px}
.paths{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.path{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:16px;display:grid;gap:8px;text-align:left;font:inherit;color:inherit;cursor:pointer}
.path:hover,.path[aria-pressed="true"]{border-color:var(--accent)}
.path:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.path h3{margin:0;font-size:16px}
.steps{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-variant-numeric:tabular-nums;font-size:13px;font-weight:600;color:var(--accent)}
.steps span.s{border:1px solid var(--line);border-radius:4px;padding:1px 6px;background:var(--bg)}
.path p{font-size:13.5px;color:var(--muted)}
.guide{display:grid;gap:10px;max-width:74ch}
.guide ol{margin:0;padding-left:20px;display:grid;gap:6px}
footer{font-size:12px;color:var(--muted);max-width:74ch;display:grid;gap:6px}
</style>
"""

def cell_name(c):
    k = next(x for x in KNOWLEDGE if x[0] == c[0]); p = next(x for x in PROCESSES if x[0] == c[1])
    return f"{k[1].replace(' 지식', '')}·{p[1]}"

def payload():
    common = {k + p: {"acts": [[a, []] for a in acts], "out": out} for k, row in CELLS.items() for p, (acts, out) in row.items()}
    subs = []
    for s in SUBJECTS:
        full = lambda c: f"{s['prefix']}-{c}"
        subs.append({
            "id": s["id"], "name": s["name"], "area": s["area"],
            "standards": [[full(c), t, cells] for c, t, cells in s["standards"]],
            "cells": {k: {"acts": [[a, [full(c) for c in cs.split(',') if c]] for a, cs in acts]} for k, acts in s["cells"].items()},
        })
    return {"processes": PROCESSES, "knowledge": KNOWLEDGE, "common": common, "subjects": subs,
            "names": {k[0] + p[0]: cell_name(k[0] + p[0]) for k in KNOWLEDGE for p in PROCESSES}}

def body():
    o = ['<div class="wrap">', '<header>',
         '<span class="eyebrow">BLOOM’S REVISED TAXONOMY × 2022 개정 교육과정</span>',
         '<h1>블룸의 개정 교육목표 분류로 보는 학생 탐구활동 추천 매트릭스</h1>',
         '<p class="lead">지식 차원 4가지와 인지 과정 6가지를 교차한 24칸에 탐구활동을 추천합니다. 과목을 고르면 2022 개정 교육과정 성취기준을 칸에 배치하고, 그 성취기준에 맞춘 과목별 활동을 보여 줍니다.</p>',
         '</header>',
         '<section aria-label="과목 선택"><div class="tabs" role="tablist" id="tabs"></div><p class="subject-note" id="subject-note"></p></section>',
         '<section><div class="scroller"><table class="mx" id="mx">', '<thead><tr><th class="corner" scope="col">지식 차원 ↓ / 인지 과정 →</th>']
    for code, ko, en, d, v in PROCESSES:
        o.append(f'<th scope="col"><span class="en">{code}. {en}</span><span class="ko">{ko}</span><span class="def">{E(d)}</span><span class="vb">{E(v)}</span></th>')
    o.append('</tr></thead><tbody>')
    for kc, ko, en, d in KNOWLEDGE:
        o.append(f'<tr><th scope="row" class="dim"><span class="en">{kc}. {en}</span><span class="ko">{ko}</span><span class="def">{E(d)}</span></th>')
        for pc, *_ in PROCESSES:
            acts, out = CELLS[kc][pc]
            lis = ''.join(f'<li>{E(a)}</li>' for a in acts)
            o.append(f'<td class="p{pc}" id="c-{kc}{pc}"><span class="code">{kc}{pc}</span><ul>{lis}</ul><div class="out"><b>산출물</b> {E(out)}</div></td>')
        o.append('</tr>')
    o.append('</tbody></table></div>')
    o.append('<p class="axis">오른쪽으로 갈수록 고차원 사고, 아래로 갈수록 추상적인 지식입니다. 칸 색이 진할수록 인지 부담이 큰 활동입니다. 활동 옆 번호는 관련 성취기준이며, 마우스를 올리면 원문이 나옵니다.</p></section>')
    o.append('<section id="std-section" hidden><h2 id="std-title">성취기준 배치</h2><p class="lead" style="margin-bottom:12px">성취기준의 동사(인지 과정)와 목적어(지식 차원)를 기준으로 칸을 정했습니다. 테두리가 진한 칸이 주된 칸입니다. 칸 번호를 누르면 표에서 위치를 보여 줍니다.</p><div class="scroller"><table class="st"><thead><tr><th scope="col">코드</th><th scope="col">성취기준</th><th scope="col">칸</th></tr></thead><tbody id="std-body"></tbody></table></div></section>')
    o.append('<section><h2>탐구 경로 예시</h2><p class="lead" style="margin-bottom:16px">한 학기 탐구를 몇 칸의 순서로 묶은 예시입니다. 경로를 누르면 표에 해당 칸이 표시되고, 과목을 바꿔도 같은 칸의 과목별 활동을 볼 수 있습니다.</p><div class="paths">')
    for i, (name, steps, desc) in enumerate(PATHS):
        st = '<span aria-hidden="true">→</span>'.join(f'<span class="s">{s} {E(cell_name(s))}</span>' for s in steps)
        o.append(f'<button type="button" class="path" id="path-{i}" aria-pressed="false" data-cells="{" ".join(steps)}"><h3>{E(name)}</h3><div class="steps">{st}</div><p>{E(desc)}</p></button>')
    o.append('</div></section>')
    o.append('''<section class="guide"><h2>활용 안내</h2><ol>
<li><b>성취기준 찾기:</b> 과목을 고르고 아래 성취기준 목록에서 수업할 성취기준의 칸을 확인합니다. 예: “이차함수의 최대, 최소를 탐구하고, 이를 실생활과 연결하여…” → 개념적 지식 × 적용(B3).</li>
<li><b>활동 고르기:</b> 그 칸의 과목별 활동을 고르거나, 전 과목 공통 활동을 과목 내용에 맞게 바꿉니다.</li>
<li><b>단계 배치:</b> 주된 칸의 왼쪽이나 위쪽 칸에서 시작해 2~4칸을 이어 탐구 경로를 만듭니다. 성취기준이 없는 칸의 활동은 기초 다지기나 성찰 활동으로 덧붙이면 됩니다.</li>
<li><b>평가 정렬:</b> 주된 칸의 활동 결과물을 수행평가 대상으로 삼으면 성취기준, 활동, 평가가 같은 칸에 맞춰집니다.</li>
</ol></section>''')
    o.append('<footer><p>성취기준: 교육부 고시 제2022-33호 2022 개정 교육과정, 고등학교 1학년 공통과목. 원문은 국가교육과정정보센터(NCIC)에서 확인할 수 있습니다. 통합과학1은 원문을 확인한 성취기준만 실었습니다.</p><p>분류 틀: Anderson, L. W., &amp; Krathwohl, D. R. (Eds.). (2001). <i>A Taxonomy for Learning, Teaching, and Assessing.</i> Longman. 성취기준의 칸 배치는 교사 판단을 돕기 위한 예시입니다.</p></footer>')
    o.append('</div>')
    o.append('<script>var DATA=' + json.dumps(payload(), ensure_ascii=False) + ';</script>')
    o.append(JS)
    return '\n'.join(o)

JS = r'''<script>
(function(){
  var esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
  var short=function(c){return c.replace(/^\d+\D+(\d-)?/,'')};
  var TEXT={}; DATA.subjects.forEach(function(s){s.standards.forEach(function(x){TEXT[x[0]]=x[1]})});
  var chip=function(c,cls){return '<span class="ref'+cls+'" tabindex="0" data-code="'+esc(c)+'" aria-label="'+esc(c+' '+(TEXT[c]||''))+'">'+esc(short(c))+'</span>'};
  var tip=document.createElement('div');tip.className='tip';tip.hidden=true;tip.setAttribute('role','tooltip');document.body.appendChild(tip);
  function showTip(el){var c=el.dataset.code;tip.innerHTML='<b>['+esc(c)+']</b>'+esc(TEXT[c]||'');tip.hidden=false;
    var r=el.getBoundingClientRect(),w=tip.offsetWidth,h=tip.offsetHeight;
    var x=Math.min(Math.max(16,r.left+r.width/2-w/2),window.innerWidth-w-16),y=r.top-h-8;if(y<8)y=r.bottom+8;
    tip.style.left=x+'px';tip.style.top=y+'px';}
  function hideTip(){tip.hidden=true}
  document.addEventListener('mouseover',function(e){var el=e.target.closest('.ref[data-code]');if(el)showTip(el)});
  document.addEventListener('mouseout',function(e){if(e.target.closest('.ref[data-code]'))hideTip()});
  document.addEventListener('focusin',function(e){var el=e.target.closest('.ref[data-code]');if(el)showTip(el)});
  document.addEventListener('focusout',hideTip);window.addEventListener('scroll',hideTip,true);
  var tabs=document.getElementById('tabs'), note=document.getElementById('subject-note');
  var views=[{id:'common',name:'전 과목 공통',area:''}].concat(DATA.subjects);
  views.forEach(function(v){
    var b=document.createElement('button');b.type='button';b.className='tab';b.id='tab-'+v.id;b.setAttribute('role','tab');
    b.innerHTML=esc(v.name)+(v.standards?'<small>'+v.standards.length+'</small>':'');
    b.addEventListener('click',function(){location.hash=v.id});tabs.appendChild(b);
  });
  function clearMarks(){document.querySelectorAll('.mx td.on').forEach(function(t){t.classList.remove('on')});
    document.querySelectorAll('.path').forEach(function(x){x.setAttribute('aria-pressed','false')});}
  function mark(cells){clearMarks();cells.forEach(function(c){var t=document.getElementById('c-'+c);if(t)t.classList.add('on')});
    var f=document.getElementById('c-'+cells[0]);if(f)f.scrollIntoView({behavior:'smooth',block:'center',inline:'center'});}
  function render(){
    var id=(location.hash||'').slice(1); var v=views.filter(function(x){return x.id===id})[0]||views[0];
    views.forEach(function(x){document.getElementById('tab-'+x.id).setAttribute('aria-selected',x===v?'true':'false')});
    clearMarks();
    var byCell={};
    if(v.standards){v.standards.forEach(function(s){s[2].forEach(function(c,i){(byCell[c]=byCell[c]||[]).push({code:s[0],main:i===0})})});}
    Object.keys(DATA.names).forEach(function(k){
      var td=document.getElementById('c-'+k), cell=v.standards?v.cells[k]:DATA.common[k];
      var h='<span class="code">'+k+'</span><ul>'+cell.acts.map(function(a){
        return '<li>'+esc(a[0])+a[1].map(function(c){return chip(c,'')}).join('')+'</li>'}).join('')+'</ul>';
      if(!v.standards) h+='<div class="out"><b>산출물</b> '+esc(cell.out)+'</div>';
      else if(byCell[k]) h+='<div class="stds"><b>성취기준</b> '+byCell[k].map(function(x){return chip(x.code,x.main?' main':'')}).join('')+'</div>';
      td.innerHTML=h;
    });
    var sec=document.getElementById('std-section');
    if(v.standards){
      sec.hidden=false;
      note.textContent=v.name+' 성취기준 '+v.standards.length+'개를 칸에 배치했습니다. 활동 옆 번호는 성취기준 코드의 뒷자리이고, 마우스를 올리거나 누르면 성취기준 원문이 나옵니다(예: '+short(v.standards[0][0])+' → '+v.standards[0][0]+').';
      document.getElementById('std-title').textContent=v.name+' 성취기준 배치';
      document.getElementById('std-body').innerHTML=v.standards.map(function(s){
        return '<tr><td class="c">['+esc(s[0])+']</td><td>'+esc(s[1])+'</td><td class="k">'+s[2].map(function(c,i){
          return '<button type="button" class="std-cell'+(i===0?' main':'')+'" data-cells="'+c+'">'+c+'<span>'+esc(DATA.names[c])+'</span></button>'}).join('')+'</td></tr>'}).join('');
    } else { sec.hidden=true; note.textContent='과목 공통으로 쓸 수 있는 기본 활동과 산출물입니다. 과목을 고르면 성취기준에 맞춘 활동으로 바뀝니다.'; }
  }
  document.addEventListener('click',function(e){
    var r=e.target.closest('.ref[data-code]');if(r){showTip(r);return;}
    var b=e.target.closest('.std-cell');if(b){mark([b.dataset.cells]);return;}
    var p=e.target.closest('.path');if(p){var on=p.getAttribute('aria-pressed')!=='true';clearMarks();
      if(on){mark(p.dataset.cells.split(' '));p.setAttribute('aria-pressed','true');}}
  });
  window.addEventListener('hashchange',render);render();
})();
</script>'''

CDN = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">'

def embedded(text):
    # 아티팩트는 외부 글꼴 호스트를 막으므로 페이지에 쓰인 글자만 남긴 Pretendard를 data URI로 넣는다
    src = os.environ['PRETENDARD_WOFF2']
    open('_chars.txt', 'w').write(text + '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
    subprocess.run(['pyftsubset', src, '--text-file=_chars.txt', '--flavor=woff2', '--output-file=_sub.woff2', '--layout-features=*'], check=True)
    d = base64.b64encode(open('_sub.woff2', 'rb').read()).decode()
    os.remove('_chars.txt'); os.remove('_sub.woff2')
    return '<style>@font-face{font-family:"Pretendard Variable";font-weight:45 920;font-style:normal;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2-variations")}</style>' % d

page = body()
open(os.path.join(ROOT, 'index.html'), 'w').write('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<style>body{margin:0}</style>\n' + CSS.replace('%%FONT%%', CDN) + '</head>\n<body>\n' + page + '\n</body>\n</html>\n')
if os.environ.get('PRETENDARD_WOFF2'):
    open('matrix.html', 'w').write(CSS.replace('%%FONT%%', embedded(CSS + page)) + page)

# ---------- Markdown ----------
def md_matrix(get):
    rows = ['| 지식 \\ 인지 | ' + ' | '.join(f'{c}. {ko}' for c, ko, *_ in PROCESSES) + ' |', '|---' * 7 + '|']
    for kc, ko, *_ in KNOWLEDGE:
        rows.append('| ' + ' | '.join([f'**{kc}. {ko}**'] + [f'`{kc}{pc}` ' + get(kc + pc) for pc, *_ in PROCESSES]) + ' |')
    return rows

LINKS = ['## 바로가기', '',
 '| 보기 | 링크 |', '|---|---|',
 '| 웹 페이지 (GitHub Pages) | https://2023swhs3rd-a11y.github.io/matrix/ |',
 '| 웹 미리보기 (Pages 설정 전에도 열림) | https://htmlpreview.github.io/?https://github.com/2023swhs3rd-a11y/matrix/blob/main/index.html |',
 '| HTML 원본 | [index.html](index.html) |',
 '| 과목별 매트릭스 | ' + ' · '.join(f'[{s["name"]}](subjects/{s["id"]}.md)' for s in SUBJECTS) + ' |',
 '| 이 문서 안 | [두 축](#두-축) · [전 과목 공통 매트릭스](#전-과목-공통-매트릭스) · [탐구 경로 예시](#탐구-경로-예시) · [활용 안내](#활용-안내) |', '']

r = ['# 블룸의 개정 교육목표 분류 활용 학생 탐구활동 추천 매트릭스', '',
     'Anderson & Krathwohl(2001)의 개정 블룸 분류에서 **지식 차원(4)** × **인지 과정 차원(6)** 을 교차한 24칸에 탐구활동을 추천합니다. **2022 개정 교육과정 고1 공통과목** 6개(공통국어1, 공통수학1, 공통영어1, 통합사회1, 통합과학1, 한국사1)는 성취기준을 칸에 배치하고 과목별 활동을 따로 정리했습니다.', ''] + LINKS
r += ['## 두 축', '', '| 인지 과정 | 뜻 | 하위 과정 |', '|---|---|---|']
for c, ko, en, d, v in PROCESSES: r.append(f'| {c}. {ko} ({en}) | {d} | {v} |')
r += ['', '| 지식 차원 | 하위 유형 |', '|---|---|']
for c, ko, en, d in KNOWLEDGE: r.append(f'| {c}. {ko} ({en}) | {d} |')
r += ['', '## 과목별 매트릭스', '', '| 과목 | 성취기준 수 | 성취기준이 가장 많이 모인 칸 |', '|---|---|---|']
for s in SUBJECTS:
    cnt = {}
    for _, _, cells in s['standards']: cnt[cells[0]] = cnt.get(cells[0], 0) + 1
    top = sorted(cnt.items(), key=lambda x: -x[1])[:2]
    r.append(f'| [{s["name"]}](subjects/{s["id"]}.md) | {len(s["standards"])} | ' + ', '.join(f'{k}({cell_name(k)}) {n}개' for k, n in top) + ' |')
r += ['', '## 전 과목 공통 매트릭스', '', '각 칸: 추천 활동 · **산출물**', '']
r += md_matrix(lambda k: '<br>'.join('• ' + a for a in CELLS[k[0]][k[1]][0]) + f'<br>**산출물:** {CELLS[k[0]][k[1]][1]}')
r += ['', '## 탐구 경로 예시', '']
for name, steps, desc in PATHS:
    r.append(f'- **{name}**: ' + ' → '.join(f'{s}({cell_name(s)})' for s in steps) + f'  \n  {desc}')
r += ['', '## 활용 안내', '',
 '1. **성취기준 찾기:** 과목별 문서에서 수업할 성취기준의 칸을 확인합니다. 예: “이차함수의 최대, 최소를 탐구하고, 이를 실생활과 연결하여…” → 개념적 지식 × 적용(B3).',
 '2. **활동 고르기:** 그 칸의 과목별 활동을 고르거나, 전 과목 공통 활동을 과목 내용에 맞게 바꿉니다.',
 '3. **단계 배치:** 주된 칸의 왼쪽이나 위쪽 칸에서 시작해 2~4칸을 이어 탐구 경로를 만듭니다.',
 '4. **평가 정렬:** 주된 칸의 활동 결과물을 수행평가 대상으로 삼아 성취기준, 활동, 평가를 같은 칸에 맞춥니다.', '',
 '## 출처와 수정 방법', '',
 '- 성취기준: 교육부 고시 제2022-33호 2022 개정 교육과정. 원문은 [국가교육과정정보센터(NCIC)](https://www.ncic.re.kr)에서 확인할 수 있습니다. 통합과학1은 원문을 확인한 성취기준만 실었습니다.',
 '- 칸 배치는 성취기준의 동사(인지 과정)와 목적어(지식 차원)를 기준으로 한 예시이며 교사 판단에 따라 바꿀 수 있습니다.',
 '- 내용은 `tools/data.py`(공통)와 `tools/subjects.py`(과목별)에 있습니다. 고친 뒤 `cd tools && python3 gen.py`를 실행하면 `index.html`, `README.md`, `subjects/*.md`가 다시 만들어집니다.', '',
 'Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom’s Taxonomy of Educational Objectives.* Longman.', '']
open(os.path.join(ROOT, 'README.md'), 'w').write('\n'.join(r))

os.makedirs(os.path.join(ROOT, 'subjects'), exist_ok=True)
for s in SUBJECTS:
    p = s['prefix']
    m = [f'# {s["name"]} 탐구활동 추천 매트릭스', '',
         f'2022 개정 교육과정 {s["name"]} 성취기준 {len(s["standards"])}개를 개정 블룸 분류 칸에 배치하고, 칸마다 과목에 맞춘 탐구활동을 정리했습니다. [전체 README로 돌아가기](../README.md)', '',
         '## 성취기준 배치', '', '주된 칸은 굵게 표시했습니다.', '', '| 코드 | 성취기준 | 칸 |', '|---|---|---|']
    for c, t, cells in s['standards']:
        m.append(f'| [{p}-{c}] | {t} | ' + ', '.join((f'**{k}** {cell_name(k)}' if i == 0 else f'{k} {cell_name(k)}') for i, k in enumerate(cells)) + ' |')
    by = {}
    for c, _, cells in s['standards']:
        for k in cells: by.setdefault(k, []).append(c)
    m += ['', '## 과목별 활동 매트릭스', '', '활동 뒤 괄호는 관련 성취기준 코드 뒷자리, 칸 끝의 “성취기준”은 그 칸에 배치된 성취기준입니다.', '']
    def get(k, s=s):
        acts = '<br>'.join('• ' + a + (f' ({cs.replace(",", ", ")})' if cs else '') for a, cs in s['cells'][k])
        return acts + (f'<br>**성취기준:** {", ".join(by[k])}' if k in by else '')
    m += md_matrix(get)
    m.append('')
    open(os.path.join(ROOT, 'subjects', f'{s["id"]}.md'), 'w').write('\n'.join(m))
print('ok')
