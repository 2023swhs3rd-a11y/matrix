import sys, html
sys.path.insert(0, '.')
from data import *
E = html.escape

CSS = """
<title>블룸 탐구활동 매트릭스</title>
<meta name="claude:viewport-fit-sides" content="cover">
%%FONT%%
<style>
/* 레이아웃: 상단 머리말 → 4×6 매트릭스(가로 스크롤 컨테이너) → 탐구 경로 예시 → 활용 안내 */
:root{
  --bg:#f6f7f9; --surface:#ffffff; --fg:#1d2430; --muted:#5b6575; --line:#d9dee6;
  --accent:#2f5d8a;
  --l1:#eef3f8; --l2:#e3ecf5; --l3:#d6e4f1; --l4:#c8dbec; --l5:#b9d1e8; --l6:#a9c6e3;
  --hl:#f2c14e;
  --display:"Pretendard Variable", Pretendard, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
  --body:"Pretendard Variable", Pretendard, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#12161c; --surface:#1a2029; --fg:#e4e8ee; --muted:#9aa4b2; --line:#2c3542; --accent:#8fb8e0;
  --l1:#18212c; --l2:#1b2632; --l3:#1e2b39; --l4:#213041; --l5:#243649; --l6:#283c52; --hl:#d9a93a; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#12161c; --surface:#1a2029; --fg:#e4e8ee; --muted:#9aa4b2; --line:#2c3542; --accent:#8fb8e0;
  --l1:#18212c; --l2:#1b2632; --l3:#1e2b39; --l4:#213041; --l5:#243649; --l6:#283c52; --hl:#d9a93a; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.6;word-break:keep-all;overflow-wrap:break-word}
.wrap{max-width:1280px;margin:0 auto;padding-block:40px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:40px}
header{display:grid;gap:10px;max-width:70ch}
.eyebrow{font-size:12px;letter-spacing:.08em;color:var(--accent);font-weight:600}
h1{font-family:var(--display);font-weight:800;letter-spacing:-.02em;font-size:clamp(26px,4vw,38px);line-height:1.25;margin:0;text-wrap:balance}
h2{font-family:var(--display);font-weight:700;letter-spacing:-.01em;font-size:22px;margin:0 0 4px;text-wrap:balance}
p{margin:0}
.lead{color:var(--muted)}
.scroller{overflow-x:auto;border:1px solid var(--line);border-radius:6px;background:var(--surface)}
table{border-collapse:collapse;width:100%;min-width:1080px;table-layout:fixed}
th,td{border:1px solid var(--line);vertical-align:top;text-align:left;padding:12px}
thead th{background:var(--surface);font-weight:600}
thead th .ko{display:block;font-family:var(--display);font-size:18px}
thead th .en,.dim .en{font-size:11px;letter-spacing:.06em;color:var(--muted);text-transform:uppercase}
thead th .def{display:block;font-weight:400;font-size:12px;color:var(--muted);margin-top:4px;line-height:1.45}
thead th .vb{display:block;font-weight:500;font-size:12px;color:var(--accent);margin-top:6px}
.corner{width:150px;font-size:12px;color:var(--muted);font-weight:500}
.dim{background:var(--surface)}
.dim .ko{display:block;font-family:var(--display);font-size:17px;font-weight:700}
.dim .def{display:block;font-size:12px;color:var(--muted);margin-top:4px;line-height:1.45}
td{font-size:13.5px}
td.p1{background:var(--l1)} td.p2{background:var(--l2)} td.p3{background:var(--l3)}
td.p4{background:var(--l4)} td.p5{background:var(--l5)} td.p6{background:var(--l6)}
.code{font-size:11px;font-weight:600;color:var(--accent);font-variant-numeric:tabular-nums;letter-spacing:.04em}
td ul{margin:4px 0 8px;padding-left:16px;display:grid;gap:4px}
.out{font-size:12px;color:var(--muted);border-top:1px dashed var(--line);padding-top:6px}
.out b{font-weight:600;color:var(--fg)}
td.on{outline:3px solid var(--hl);outline-offset:-3px}
.axis{font-size:12px;color:var(--muted);margin-top:8px}
.paths{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
.path{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:16px;display:grid;gap:8px;text-align:left;font:inherit;color:inherit;cursor:pointer}
.path:hover,.path[aria-pressed="true"]{border-color:var(--accent)}
.path:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.path h3{margin:0;font-size:16px}
.steps{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-variant-numeric:tabular-nums;font-size:13px;font-weight:600;color:var(--accent)}
.steps span.s{border:1px solid var(--line);border-radius:4px;padding:1px 6px;background:var(--bg)}
.path p{font-size:13.5px;color:var(--muted)}
.guide{display:grid;gap:10px;max-width:72ch}
.guide ol{margin:0;padding-left:20px;display:grid;gap:6px}
footer{font-size:12px;color:var(--muted);max-width:72ch}
</style>
"""

def cell_name(c):
    k = next(x for x in KNOWLEDGE if x[0]==c[0]); p = next(x for x in PROCESSES if x[0]==c[1])
    return f"{k[1].replace(' 지식','')}·{p[1]}"

def body():
    o = ['<div class="wrap">', '<header>',
         '<span class="eyebrow">BLOOM’S REVISED TAXONOMY · ANDERSON &amp; KRATHWOHL (2001)</span>',
         '<h1>블룸의 개정 교육목표 분류로 보는 학생 탐구활동 추천 매트릭스</h1>',
         '<p class="lead">지식 차원 4가지와 인지 과정 차원 6가지를 교차한 24칸에 칸마다 추천 탐구활동과 산출물을 넣은 기본형입니다. 칸 번호(A1~D6)로 활동을 지정하고, 아래 탐구 경로를 눌러 활동 순서를 표에서 확인할 수 있습니다.</p>',
         '</header>', '<section>', '<div class="scroller"><table>', '<thead><tr><th class="corner" scope="col">지식 차원 ↓ / 인지 과정 →</th>']
    for code,ko,en,d,v in PROCESSES:
        o.append(f'<th scope="col"><span class="en">{code}. {en}</span><span class="ko">{ko}</span><span class="def">{E(d)}</span><span class="vb">{E(v)}</span></th>')
    o.append('</tr></thead><tbody>')
    for kc,ko,en,d in KNOWLEDGE:
        o.append(f'<tr><th scope="row" class="dim"><span class="en">{kc}. {en}</span><span class="ko">{ko}</span><span class="def">{E(d)}</span></th>')
        for pc,*_ in PROCESSES:
            acts,out = CELLS[kc][pc]
            lis = ''.join(f'<li>{E(a)}</li>' for a in acts)
            o.append(f'<td class="p{pc}" id="c-{kc}{pc}"><span class="code">{kc}{pc}</span><ul>{lis}</ul><div class="out"><b>산출물</b> {E(out)}</div></td>')
        o.append('</tr>')
    o.append('</tbody></table></div>')
    o.append('<p class="axis">오른쪽으로 갈수록 고차원 사고(인지 과정), 아래로 갈수록 추상적인 지식입니다. 칸 색이 진할수록 인지 부담이 큰 활동입니다.</p></section>')
    o.append('<section><h2>탐구 경로 예시</h2><p class="lead" style="margin-bottom:16px">한 학기 탐구를 몇 칸의 순서로 묶은 예시입니다. 경로를 누르면 표에 해당 칸이 표시됩니다.</p><div class="paths">')
    for i,(name,steps,desc) in enumerate(PATHS):
        st = '<span aria-hidden="true">→</span>'.join(f'<span class="s">{s} {E(cell_name(s))}</span>' for s in steps)
        o.append(f'<button type="button" class="path" id="path-{i}" aria-pressed="false" data-cells="{" ".join(steps)}"><h3>{E(name)}</h3><div class="steps">{st}</div><p>{E(desc)}</p></button>')
    o.append('</div></section>')
    o.append('''<section class="guide"><h2>활용 안내</h2><ol>
<li><b>목표 진술:</b> 성취기준을 “명사(지식 차원) + 동사(인지 과정)”로 나누면 해당 칸이 정해집니다. 예: “광합성의 원리를 설명할 수 있다” → 개념적 지식 × 이해(B2).</li>
<li><b>활동 선택:</b> 칸의 추천 활동 중 하나를 고르고 교과 주제에 맞게 바꿉니다. 같은 칸이면 교과가 달라도 활동 형태는 그대로 쓸 수 있습니다.</li>
<li><b>단계 배치:</b> 왼쪽 위(A1)에서 오른쪽 아래(D6) 방향으로 2~4칸을 이어 탐구 경로를 만듭니다. 꼭 한 칸씩 순서대로 갈 필요는 없습니다.</li>
<li><b>평가 정렬:</b> 산출물 칸에 적힌 결과물을 평가 대상으로 삼으면 목표, 활동, 평가가 같은 칸에 맞춰집니다.</li>
</ol></section>''')
    o.append('<footer>참고: Anderson, L. W., &amp; Krathwohl, D. R. (Eds.). (2001). <i>A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom’s Taxonomy of Educational Objectives.</i> Longman. 인지 과정 6단계의 마지막 단계(Create)는 국내 문헌에서 “창안” 또는 “창조”로 번역됩니다.</footer>')
    o.append('</div>')
    o.append('''<script>
document.querySelectorAll('.path').forEach(function(b){b.addEventListener('click',function(){
  var on=b.getAttribute('aria-pressed')!=='true';
  document.querySelectorAll('.path').forEach(function(x){x.setAttribute('aria-pressed','false')});
  document.querySelectorAll('td.on').forEach(function(t){t.classList.remove('on')});
  if(on){b.setAttribute('aria-pressed','true');b.dataset.cells.split(' ').forEach(function(c){var t=document.getElementById('c-'+c);if(t)t.classList.add('on')});
    var first=document.getElementById('c-'+b.dataset.cells.split(' ')[0]);if(first)first.scrollIntoView({behavior:'smooth',block:'center',inline:'center'});}
})});
</script>''')
    return '\n'.join(o)

import base64, subprocess, os
CDN = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">'
def embedded():
    # 아티팩트는 외부 글꼴 호스트를 막으므로 페이지에 쓰인 글자만 남긴 Pretendard를 data URI로 넣는다
    src = os.environ.get('PRETENDARD_WOFF2')
    if not src: return CDN
    open('_chars.txt','w').write(CSS + body() + '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
    subprocess.run(['pyftsubset', src, '--text-file=_chars.txt', '--flavor=woff2', '--output-file=_sub.woff2', '--layout-features=*'], check=True)
    d = base64.b64encode(open('_sub.woff2','rb').read()).decode()
    os.remove('_chars.txt'); os.remove('_sub.woff2')
    return '<style>@font-face{font-family:"Pretendard Variable";font-weight:45 920;font-style:normal;font-display:swap;src:url(data:font/woff2;base64,%s) format("woff2-variations")}</style>' % d
FULL = CSS
CSS = FULL.replace('%%FONT%%', CDN)
emb = FULL.replace('%%FONT%%', embedded())
open('matrix.html','w').write(emb + body())
open('index.html','w').write('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<style>body{margin:0}</style>\n' + CSS + '</head>\n<body>\n' + body() + '\n</body>\n</html>\n')

# README
r = ['# 블룸의 개정 교육목표 분류 활용 학생 탐구활동 추천 매트릭스', '',
     'Anderson & Krathwohl(2001)의 개정 블룸 분류에서 **지식 차원(4)** × **인지 과정 차원(6)** 을 교차한 24칸에 추천 탐구활동과 산출물을 넣은 기본형입니다. 보기 좋은 표는 [`index.html`](index.html)을 브라우저로 열어 확인하세요.', '',
     '## 두 축', '', '| 인지 과정 | 뜻 | 하위 과정 |', '|---|---|---|']
for c,ko,en,d,v in PROCESSES: r.append(f'| {c}. {ko} ({en}) | {d} | {v} |')
r += ['', '| 지식 차원 | 하위 유형 |', '|---|---|']
for c,ko,en,d in KNOWLEDGE: r.append(f'| {c}. {ko} ({en}) | {d} |')
r += ['', '## 매트릭스', '', '각 칸: 추천 활동 · **산출물**', '',
      '| 지식 \\ 인지 | ' + ' | '.join(f'{c}. {ko}' for c,ko,*_ in PROCESSES) + ' |', '|---' * 7 + '|']
for kc,ko,*_ in KNOWLEDGE:
    row = [f'**{kc}. {ko}**']
    for pc,*_ in PROCESSES:
        acts,out = CELLS[kc][pc]
        row.append(f'`{kc}{pc}` ' + '<br>'.join('• '+a for a in acts) + f'<br>**산출물:** {out}')
    r.append('| ' + ' | '.join(row) + ' |')
r += ['', '## 탐구 경로 예시', '']
for name,steps,desc in PATHS:
    r.append(f'- **{name}**: ' + ' → '.join(f'{s}({cell_name(s)})' for s in steps) + f'  \n  {desc}')
r += ['', '## 활용 안내', '',
 '1. **목표 진술:** 성취기준을 “명사(지식 차원) + 동사(인지 과정)”로 나누면 해당 칸이 정해집니다. 예: “광합성의 원리를 설명할 수 있다” → 개념적 지식 × 이해(B2).',
 '2. **활동 선택:** 칸의 추천 활동 중 하나를 고르고 교과 주제에 맞게 바꿉니다.',
 '3. **단계 배치:** 왼쪽 위(A1)에서 오른쪽 아래(D6) 방향으로 2~4칸을 이어 탐구 경로를 만듭니다.',
 '4. **평가 정렬:** 산출물을 평가 대상으로 삼아 목표, 활동, 평가를 같은 칸에 맞춥니다.', '',
 '## 참고', '', 'Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom’s Taxonomy of Educational Objectives.* Longman.', '']
open('README.md','w').write('\n'.join(r))
