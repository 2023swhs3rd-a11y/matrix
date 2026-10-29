# index.html, README.md, subjects/*.md 생성 스크립트 (tools 폴더에서 python3 gen.py)
# PRETENDARD_WOFF2=<PretendardVariable.woff2 경로>를 주면 글꼴을 넣은 미리보기용 matrix.html도 만든다.
import sys, html, json, os, base64, subprocess, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import PROCESSES, KNOWLEDGE, CELLS, PATHS, TOPIC_TEMPLATES, TOPIC_LENS, TOPIC_RELATED, CELL_DETAIL
from subjects import SUBJECTS as _S1
from subjects_common2 import SUBJECTS_COMMON2
from subjects_general import SUBJECTS_GENERAL
from subjects_career import SUBJECTS_CAREER
from subjects_convergence import SUBJECTS_CONVERGENCE
# 고1 공통은 1학기 과목 바로 뒤에 같은 교과의 2학기 과목을 두고, 과학탐구실험은 끝에 둔다
_PAIR = {s.get('pair', s['id']): s for s in SUBJECTS_COMMON2}
_S1 = [x for s in _S1 for x in (s, _PAIR.pop(s['id'], None)) if x] + list(_PAIR.values())
for _s in _S1: _s.setdefault('group', '고1 공통')
SUBJECTS = _S1 + SUBJECTS_GENERAL + SUBJECTS_CAREER + SUBJECTS_CONVERGENCE
assert len({s['id'] for s in SUBJECTS}) == len(SUBJECTS), '과목 id가 겹칩니다'
GROUPS = list(dict.fromkeys(s['group'] for s in SUBJECTS))
def code(s, c): return f"{s['prefix']}{s.get('sep', '-')}{c}"
E = html.escape
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

CSS = """
<title>블룸 교과탐구활동 매트릭스</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><path d='M4 13c9-4 19-3 26 2v38c-7-5-17-6-26-2z' fill='%232b67a8'/><path d='M60 13c-9-4-19-3-26 2v38c7-5 17-6 26-2z' fill='%235b8fd0'/><circle cx='41' cy='36' r='12' fill='%23fff' stroke='%231d2733' stroke-width='5'/><path d='M50 45l9 9' stroke='%231d2733' stroke-width='7' stroke-linecap='round'/></svg>">
<meta name="claude:viewport-fit-sides" content="cover">
%%FONT%%
<style>
/* 레이아웃: 머리말 → 과목 탭 → 4×6 매트릭스(가로 스크롤) → 과목 성취기준 목록 → 탐구 경로 → 활용 안내 */
:root{
  --bg:#f6f7f9; --surface:#ffffff; --fg:#1d2430; --muted:#5b6575; --line:#d9dee6;
  --accent-ink:#ffffff;
  --c-base:#3f5a78; --c-kor:#b0413a; --c-math:#2b67a8; --c-eng:#7046a8; --c-soc:#9a5b00; --c-sci:#1f7a52; --c-his:#845537; --c-eth:#5b6a1e;
  --hl:#f2c14e;
  --display:"Pretendard Variable", Pretendard, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
  --body:"Pretendard Variable", Pretendard, -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#12161c; --surface:#1a2029; --fg:#e4e8ee; --muted:#9aa4b2; --line:#2c3542; --accent-ink:#0f1620;
  --c-base:#9fb6d0; --c-kor:#ef9a8f; --c-math:#8ab8ec; --c-eng:#bfa3e6; --c-soc:#e9b067; --c-sci:#7fd0a7; --c-his:#d1a587; --c-eth:#c4d27f; --hl:#d9a93a; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#12161c; --surface:#1a2029; --fg:#e4e8ee; --muted:#9aa4b2; --line:#2c3542; --accent-ink:#0f1620;
  --c-base:#9fb6d0; --c-kor:#ef9a8f; --c-math:#8ab8ec; --c-eng:#bfa3e6; --c-soc:#e9b067; --c-sci:#7fd0a7; --c-his:#d1a587; --c-eth:#c4d27f; --hl:#d9a93a; color-scheme:dark}
/* 교과(국어·수학·영어·사회·과학·역사)마다 강조색 하나; 표의 칸 농도와 번호 배경은 그 색에서 섞어 만든다 */
body,.tab{--accent:var(--c-base)}
.a-kor{--accent:var(--c-kor)} .a-math{--accent:var(--c-math)} .a-eng{--accent:var(--c-eng)}
.a-soc{--accent:var(--c-soc)} .a-sci{--accent:var(--c-sci)} .a-his{--accent:var(--c-his)} .a-eth{--accent:var(--c-eth)}
body{--chip:color-mix(in srgb,var(--accent) 14%,var(--surface));
  --l1:color-mix(in srgb,var(--accent) 5%,var(--surface)); --l2:color-mix(in srgb,var(--accent) 9%,var(--surface)); --l3:color-mix(in srgb,var(--accent) 13%,var(--surface));
  --l4:color-mix(in srgb,var(--accent) 17%,var(--surface)); --l5:color-mix(in srgb,var(--accent) 22%,var(--surface)); --l6:color-mix(in srgb,var(--accent) 27%,var(--surface))}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.6;word-break:keep-all;overflow-wrap:break-word}
.wrap{max-width:1280px;margin:0 auto;padding-block:40px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:36px}
.wrap>*{min-width:0}
header{display:grid;gap:10px;max-width:72ch}
.eyebrow{font-size:12px;letter-spacing:.08em;color:var(--accent);font-weight:600}
h1{font-family:var(--display);font-weight:800;letter-spacing:-.02em;font-size:clamp(26px,4vw,38px);line-height:1.25;margin:0;text-wrap:balance}
h2{font-family:var(--display);font-weight:700;letter-spacing:-.01em;font-size:22px;margin:0 0 4px;text-wrap:balance}
p{margin:0}
.lead{color:var(--muted)}
.picker{display:grid;gap:14px}
.topic{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.topic label{font-size:12px;font-weight:600;color:var(--muted);letter-spacing:.04em;margin-right:4px}
.topic input,.topic select,.topic button{font:inherit;font-size:14px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--fg);padding:7px 10px}
.topic input{flex:1 1 260px;min-width:0}
.topic button{background:var(--fg);color:var(--bg);border-color:var(--fg);font-weight:600;cursor:pointer}
.topic input:focus-visible,.topic select:focus-visible,.topic button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.mx .tpl{color:var(--muted);font-size:11px;font-weight:600;margin-right:4px}
.rel{margin-top:6px;font-size:12px;color:var(--muted)}
.rel b{font-weight:600;margin-right:4px}
.rel a{color:inherit}
.st td .subj{display:inline-block;font-size:12px;font-weight:600;margin-right:6px}
.areas{display:flex;flex-wrap:wrap;gap:4px;align-items:center}
.areas .sep{width:1px;height:20px;background:var(--line);margin:0 6px}
.area-tab{--accent:var(--c-base);font:inherit;font-size:15px;font-weight:700;color:var(--muted);background:none;border:1px solid transparent;border-radius:10px;padding:7px 14px;cursor:pointer}
.area-tab::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--accent);margin-right:7px;vertical-align:2px}
.area-tab small{font-weight:500;font-size:12px;margin-left:5px;opacity:.75}
.area-tab:hover{color:var(--fg)}
.area-tab[aria-selected="true"]{color:var(--fg);background:color-mix(in srgb,var(--accent) 14%,var(--surface));border-color:color-mix(in srgb,var(--accent) 45%,var(--line))}
.area-tab:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.panel{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px 28px;padding:16px 18px;border:1px solid var(--line);border-radius:12px;background:var(--surface)}
.panel[hidden]{display:none}
.col h3{margin:0 0 8px;font-size:12px;font-weight:600;color:var(--muted);letter-spacing:.04em}
.col h3 span{font-weight:400;margin-left:6px}
.col div{display:flex;flex-wrap:wrap;gap:6px}
.tab{font:inherit;font-size:14px;font-weight:600;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:999px;padding:5px 12px;cursor:pointer}
.tab::before{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--accent);margin-right:6px;vertical-align:1px}
.tab[aria-pressed="true"]::before{background:var(--accent-ink)}
h1 a{color:inherit;text-decoration:none}
h1 a:hover{text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:6px}
h1 a:focus-visible{outline:2px solid var(--accent);outline-offset:4px;border-radius:4px}
.tab small{font-weight:400;color:var(--muted);margin-left:4px}
.tab[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.tab[aria-pressed="true"] small{color:inherit;opacity:.8}
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
footer a{color:var(--fg);text-underline-offset:2px}
footer .links b{color:var(--fg);margin-right:4px}
footer{font-size:12px;color:var(--muted);max-width:74ch;display:grid;gap:6px}
.part{font-size:12px;color:var(--muted);margin-top:6px}
.part b{display:inline-block;font-size:11px;font-weight:700;color:var(--accent-ink);background:var(--accent);border-radius:4px;padding:0 5px;margin-right:4px}
.mx tbody td{cursor:pointer}
.mx tbody td:hover{box-shadow:inset 0 0 0 2px color-mix(in srgb,var(--accent) 40%,transparent)}
.more{display:block;margin-top:8px;font:inherit;font-size:12px;font-weight:600;color:var(--accent);background:none;border:1px solid color-mix(in srgb,var(--accent) 45%,var(--line));border-radius:6px;padding:3px 8px;cursor:pointer}
.more:hover{background:var(--chip)}
.more:focus-visible,.dlg-x:focus-visible,.copy:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.dlg{width:min(760px,calc(100vw - 32px));max-height:calc(100vh - 48px);padding:0;border:1px solid var(--line);border-radius:14px;background:var(--surface);color:var(--fg);box-shadow:0 18px 48px rgba(0,0,0,.25)}
.dlg::backdrop{background:rgba(15,20,28,.45)}
.dlg-head{position:sticky;top:0;display:flex;justify-content:space-between;gap:12px;align-items:flex-start;padding:18px 20px 12px;background:var(--surface);border-bottom:1px solid var(--line)}
.dlg-head h2{margin:2px 0 0;font-size:19px}
.dlg-head p{margin:4px 0 0;font-size:13px;color:var(--muted)}
.dlg-x{flex:none;font:inherit;font-size:22px;line-height:1;width:36px;height:36px;border-radius:8px;border:1px solid var(--line);background:none;color:var(--fg);cursor:pointer}
.dlg-body{padding:6px 20px 20px}
.dlg-body h3{font-size:15px;margin:18px 0 8px}
.dlg-body h3 small{font-weight:500;color:var(--muted);margin-left:6px;font-size:12px}
.callout{border-left:4px solid var(--accent);background:var(--chip);border-radius:8px;padding:10px 12px;font-size:13.5px;margin-top:14px}
.callout ul{margin:6px 0 0;padding-left:18px;display:grid;gap:3px}
.ex{border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-top:10px}
.ex h4{margin:0;font-size:14.5px}
.ex .q{margin:4px 0 6px;font-size:13.5px;color:var(--accent);font-weight:600}
.ex ol{margin:0;padding-left:18px;font-size:13.5px;display:grid;gap:2px}
.ex .o{margin:6px 0 0;font-size:12.5px;color:var(--muted)}
.rec{display:flex;gap:8px;align-items:flex-start;border:1px dashed var(--line);border-radius:10px;padding:10px 12px;margin-top:8px;font-size:13.5px;line-height:1.6}
.rec p{margin:0;flex:1}
.rec .by{display:block;font-size:11.5px;color:var(--muted);margin-bottom:2px}
.copy{flex:none;font:inherit;font-size:12px;color:var(--muted);background:none;border:1px solid var(--line);border-radius:6px;padding:2px 8px;cursor:pointer}
.dlg-note{font-size:12px;color:var(--muted);margin-top:14px}

</style>
"""

def cell_name(c):
    k = next(x for x in KNOWLEDGE if x[0] == c[0]); p = next(x for x in PROCESSES if x[0] == c[1])
    return f"{k[1].replace(' 지식', '')}·{p[1]}"

def payload():
    common = {k + p: {"acts": [[a, []] for a in acts], "out": out} for k, row in CELLS.items() for p, (acts, out) in row.items()}
    subs = []
    for s in SUBJECTS:
        full = lambda c, s=s: code(s, c)
        subs.append({
            "id": s["id"], "name": s["name"], "area": s["area"], "group": s["group"],
            "standards": [[full(c), t, cells] for c, t, cells in s["standards"]],
            "cells": {k: {"acts": [[a, [full(c) for c in cs.split(',') if c]] for a, cs in acts]} for k, acts in s["cells"].items()},
        })
    return {"processes": PROCESSES, "knowledge": KNOWLEDGE, "common": common, "subjects": subs, "topic": TOPIC_TEMPLATES, "lens": TOPIC_LENS, "related": TOPIC_RELATED, "detail": CELL_DETAIL,
            "names": {k[0] + p[0]: cell_name(k[0] + p[0]) for k in KNOWLEDGE for p in PROCESSES}}

def cell_extra(k):
    # 기억·이해·적용 칸은 수업 참여 활동을 함께 보이고, 모든 칸에 상세 보기 단추
    part = CELL_DETAIL[k]["part"]
    h = f'<div class="part"><b>수업 참여</b> {E(part[0])}</div>' if part else ''
    return h + f'<button type="button" class="more" data-cell="{k}" aria-haspopup="dialog">탐구 예시 · 기재 예시</button>'

def body():
    o = ['<div class="wrap">', '<header>',
         '<span class="eyebrow">BLOOM’S REVISED TAXONOMY × 2022 개정 교육과정</span>',
         '<h1><a href="./" id="home" title="처음 화면으로">블룸의 개정 교육목표 분류로 보는 교과탐구활동 추천 매트릭스</a></h1>',
         '<p class="lead">지식 차원 4가지와 인지 과정 6가지를 교차한 24칸에 탐구활동을 추천합니다. 과목을 고르면 2022 개정 교육과정 성취기준을 칸에 배치하고, 그 성취기준에 맞춘 과목별 활동을 보여 줍니다.</p>',
         '</header>',
         '<section aria-label="과목 선택" class="picker"><div class="areas" role="tablist" aria-label="교과" id="areas"></div><div class="panel" id="panel" hidden></div><form class="topic" id="topic-form" role="search" aria-label="주제로 활동 찾기"><label for="topic-q">주제로 찾기</label><input id="topic-q" type="search" placeholder="탐구 주제 (예: 미세플라스틱, 인공지능 윤리)" autocomplete="off"><select id="topic-f" aria-label="분야(교과)"><option value="">전체 교과</option><option>국어</option><option>수학</option><option>영어</option><option>사회</option><option>과학</option></select><button type="submit">활동 추천</button></form><p class="subject-note" id="subject-note"></p></section>',
         '<section><div class="scroller"><table class="mx" id="mx">', '<thead><tr><th class="corner" scope="col">지식 차원 ↓ / 인지 과정 →</th>']
    for code, ko, en, d, v in PROCESSES:
        o.append(f'<th scope="col"><span class="en">{code}. {en}</span><span class="ko">{ko}</span><span class="def">{E(d)}</span><span class="vb">{E(v)}</span></th>')
    o.append('</tr></thead><tbody>')
    for kc, ko, en, d in KNOWLEDGE:
        o.append(f'<tr><th scope="row" class="dim"><span class="en">{kc}. {en}</span><span class="ko">{ko}</span><span class="def">{E(d)}</span></th>')
        for pc, *_ in PROCESSES:
            acts, out = CELLS[kc][pc]
            lis = ''.join(f'<li>{E(a)}</li>' for a in acts)
            o.append(f'<td class="p{pc}" id="c-{kc}{pc}"><span class="code">{kc}{pc}</span><ul>{lis}</ul><div class="out"><b>산출물</b> {E(out)}</div>{cell_extra(kc + pc)}</td>')
        o.append('</tr>')
    o.append('</tbody></table></div>')
    o.append('<p class="axis">오른쪽으로 갈수록 고차원 사고, 아래로 갈수록 추상적인 지식입니다. 칸 색이 진할수록 인지 부담이 큰 활동입니다. 활동 옆 번호는 관련 성취기준이며, 마우스를 올리면 원문이 나옵니다. 칸을 누르면 구체적인 주제탐구 예시와 학교생활기록부 기재 예시를 볼 수 있습니다. 기억·이해·적용 칸에는 수업 참여 활동을 함께 적었습니다.</p></section>')
    o.append('<dialog class="dlg" id="cell-dlg" aria-labelledby="dlg-title"><div class="dlg-head"><div><span class="code" id="dlg-code"></span><h2 id="dlg-title"></h2><p id="dlg-sub"></p></div><button type="button" class="dlg-x" id="dlg-x" aria-label="닫기">×</button></div><div class="dlg-body" id="dlg-body"></div></dialog>')
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
<li><b>기초 단계도 기록하기:</b> 기억·이해·적용 칸의 활동은 질문하기, 자기 말로 설명하기, 정확히 기록하기, 모둠 역할 수행처럼 수업 참여 과정으로 학교생활기록부에 남길 수 있습니다. 칸을 누르면 수업 참여 활동과 기재 예시가 나옵니다.</li>
</ol></section>''')
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')
    total = sum(len(x['standards']) for x in SUBJECTS)
    o.append(f'<footer><p id="version">업데이트 {stamp} (KST) · 과목 {len(SUBJECTS)}개 · 성취기준 {total}개 · 작성자 <a href="mailto:jungsooj@korea.kr">jungsooj@korea.kr</a></p><p>성취기준: 교육부 고시 제2022-33호 2022 개정 교육과정, 고등학교 1학년 공통과목, 2·3학년 일반선택·진로선택·융합선택 과목. 공개 정리 자료에서 옮긴 뒤 과목마다 다른 공개 자료와 문장을 대조했지만(2026-10-29), 국가교육과정정보센터(NCIC) 원문과 다시 확인해 사용하세요. 원문을 구하지 못한 현대사회와 윤리, 영어 진로선택 4과목(영어 발표와 토론·심화 영어·심화 영어 독해와 작문·직무 영어), 융합선택 4과목(실생활 영어 회화·미디어 영어·역사로 탐구하는 현대 세계·윤리문제 탐구)은 아직 넣지 않았습니다.</p><p>분류 틀: Anderson, L. W., &amp; Krathwohl, D. R. (Eds.). (2001). <i>A Taxonomy for Learning, Teaching, and Assessing.</i> Longman. 성취기준의 칸 배치는 교사 판단을 돕기 위한 예시입니다.</p><p class="links"><b>원문 자료</b> <a href="https://ncic.re.kr/" target="_blank" rel="noopener">국가교육과정정보센터(NCIC)</a>: 2022 개정 교육과정 원문(교육부 고시 제2022-33호)과 교과별 교육과정 해설서 · <a href="https://www.kice.re.kr/" target="_blank" rel="noopener">한국교육과정평가원(KICE)</a>: 교육과정·평가 연구 자료 · <a href="https://www.moe.go.kr/" target="_blank" rel="noopener">교육부</a>: 교육과정 고시와 정책 자료 · <a href="https://star.moe.go.kr/" target="_blank" rel="noopener">교육부 학생평가 지원포털</a>: 성취수준과 평가 기준</p></footer>')
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
  var note=document.getElementById('subject-note');
  var views=[{id:'common',name:'전 과목 공통',area:''}].concat(DATA.subjects);
  var AREA={'국어':'kor','수학':'math','영어':'eng','사회':'soc','과학':'sci','역사':'his','도덕':'eth'};
  // 과목 고르기: 교과를 먼저 고르면 그 교과의 과목이 유형(고1 공통·일반선택·진로선택…) 열로 펼쳐진다
  var ROW={'국어':'국어','수학':'수학','영어':'영어','사회':'사회','역사':'사회','도덕':'사회','과학':'과학'};
  var ROWS=['국어','수학','영어','사회','과학'], RCLS={'국어':'kor','수학':'math','영어':'eng','사회':'soc','과학':'sci'};
  var GRADE={'고1 공통':'1학년','일반선택':'2·3학년','진로선택':'2·3학년','융합선택':'2·3학년'};
  var GROUPS=[];views.forEach(function(v){if(v.group&&GROUPS.indexOf(v.group)<0)GROUPS.push(v.group)});
  var btn={}, atab={}, cur=null, areas=document.getElementById('areas'), panel=document.getElementById('panel');
  views.forEach(function(v){
    var b=document.createElement('button');b.type='button';b.className='tab';b.id='tab-'+v.id;if(AREA[v.area])b.classList.add('a-'+AREA[v.area]);
    b.innerHTML=esc(v.name)+(v.standards?'<small>'+v.standards.length+'</small>':'');
    b.addEventListener('click',function(){location.hash=v.id});btn[v.id]=b;
  });
  function areaTab(key,label,count,cls,onclick){
    var b=document.createElement('button');b.type='button';b.className='area-tab';if(cls)b.style.setProperty('--accent','var(--c-'+cls+')');b.setAttribute('role','tab');
    b.innerHTML=esc(label)+(count?'<small>'+count+'</small>':'');b.addEventListener('click',onclick);atab[key]=b;areas.appendChild(b);
  }
  // 교과만 열어 둔 상태에서도 누르면 처음 화면으로 돌아간다(해시가 같으면 hashchange가 없으므로 직접 그린다)
  areaTab('common','전 과목 공통',0,'',function(){if(location.hash&&location.hash!=='#common')location.hash='common';else render();});
  var sep=document.createElement('span');sep.className='sep';sep.setAttribute('aria-hidden','true');areas.appendChild(sep);
  ROWS.forEach(function(r){
    var n=views.filter(function(v){return v.area&&ROW[v.area]===r}).length;
    areaTab(r,r,n,RCLS[r],function(){cur=r;buildPanel();});
  });
  function buildPanel(){
    Object.keys(atab).forEach(function(k){atab[k].setAttribute('aria-selected',(cur?k===cur:k==='common')?'true':'false')});
    panel.hidden=!cur; panel.innerHTML=''; if(!cur)return;
    GROUPS.forEach(function(g){
      var list=views.filter(function(v){return v.group===g&&ROW[v.area]===cur}); if(!list.length)return;
      var col=document.createElement('div');col.className='col';
      col.innerHTML='<h3>'+esc(g)+'<span>'+esc(GRADE[g]||'')+'</span></h3>';
      var box=document.createElement('div');box.setAttribute('role','group');box.setAttribute('aria-label',cur+' '+g);
      list.forEach(function(v){box.appendChild(btn[v.id])});col.appendChild(box);panel.appendChild(col);
    });
  }
  function clearMarks(){document.querySelectorAll('.mx td.on').forEach(function(t){t.classList.remove('on')});
    document.querySelectorAll('.path').forEach(function(x){x.setAttribute('aria-pressed','false')});}
  function mark(cells){clearMarks();cells.forEach(function(c){var t=document.getElementById('c-'+c);if(t)t.classList.add('on')});
    var f=document.getElementById('c-'+cells[0]);if(f)f.scrollIntoView({behavior:'smooth',block:'center',inline:'center'});}
  // 주제로 찾기: 칸마다 활동 틀에 주제어를 넣고, 성취기준·과목 활동에서 주제어를 찾아 함께 보여 준다
  var SUBJ={};DATA.subjects.forEach(function(s){SUBJ[s.id]=s});
  var tq=document.getElementById('topic-q'), tf=document.getElementById('topic-f');
  document.getElementById('topic-form').addEventListener('submit',function(e){e.preventDefault();
    var q=tq.value.trim();if(!q){tq.focus();return;}
    location.hash='q='+encodeURIComponent(q)+(tf.value?'&f='+encodeURIComponent(tf.value):'');});
  function tokens(q){return q.split(/[\s,·/]+/).filter(function(x){return x.length>=2})}
  // 연관어: 주제어와 같거나 서로 포함하는 사전 항목의 관련 개념. 흔한 낱말일수록 가중치를 낮춘다
  var LAREAS=['국어','수학','영어','사회','과학'], DF={};
  function df(w){if(DF[w]==null){var n=0;DATA.subjects.forEach(function(s){s.standards.forEach(function(x){if(x[1].indexOf(w)>=0)n++})});DF[w]=n}return DF[w]}
  function related(ts){var out=[];ts.forEach(function(t){
    var ks=DATA.related[t]?[t]:Object.keys(DATA.related).filter(function(k){return t.length>=2&&k.length>=2&&(k.indexOf(t)>=0||t.indexOf(k)>=0)});
    ks.forEach(function(k){DATA.related[k].forEach(function(w){if(ts.indexOf(w)<0&&out.indexOf(w)<0)out.push(w)})})});return out}
  function score(text,ts,rel){var n=0;ts.forEach(function(t){if(text.indexOf(t)>=0)n+=3});
    (rel||[]).forEach(function(w){if(text.indexOf(w)>=0){var d=df(w);n+=d<=10?1:d<=40?0.6:0.3}});return n}
  function fullChip(c){return '<span class="ref" tabindex="0" data-code="'+esc(c)+'" aria-label="'+esc(c+' '+(TEXT[c]||''))+'">'+esc(c)+'</span>'}
  function renderTopic(h){
    var p=new URLSearchParams(h), q=(p.get('q')||'').trim(), f=p.get('f')||'';
    tq.value=q;tf.value=f;cur=null;curView=null;buildPanel();
    Object.keys(atab).forEach(function(k){atab[k].setAttribute('aria-selected','false')});
    views.forEach(function(x){btn[x.id].setAttribute('aria-pressed','false')});
    clearMarks();document.body.className=RCLS[f]?'a-'+RCLS[f]:'';
    var ts=tokens(q);if(!ts.length&&q)ts=[q];var rel=related(ts);
    var subs=DATA.subjects.filter(function(s){return !f||ROW[s.area]===f});
    var stds=[],acts=[];
    subs.forEach(function(s){
      s.standards.forEach(function(x){var n=score(x[1],ts,rel);if(n>=0.6)stds.push({s:s,x:x,n:n,d:score(x[1],ts)>0})});
      Object.keys(s.cells).forEach(function(k){s.cells[k].acts.forEach(function(a){var n=score(a[0],ts,rel);if(n>=1)acts.push({s:s,k:k,a:a[0],n:n})})});
    });
    stds.sort(function(a,b){return b.n-a.n});acts.sort(function(a,b){return b.n-a.n});
    var byCell={},actCell={},aw={};
    stds.slice(0,40).forEach(function(r){var a=ROW[r.s.area];aw[a]=(aw[a]||0)+r.n});
    var order=LAREAS.slice().sort(function(a,b){return (aw[b]||0)-(aw[a]||0)});
    stds.forEach(function(r){var c=r.x[2][0];(byCell[c]=byCell[c]||[]).push(r)});
    acts.forEach(function(r){(actCell[r.k]=actCell[r.k]||[]).push(r)});
    Object.keys(DATA.names).forEach(function(k){
      var td=document.getElementById('c-'+k);
      var i=Object.keys(DATA.names).indexOf(k), L=f?[[f,DATA.lens[f][k]],['',DATA.topic[k][i%2]]]:[[order[0],DATA.lens[order[0]][k]],[order[1+i%4],DATA.lens[order[1+i%4]][k]]];
      var h='<span class="code">'+k+'</span><ul>'+L.map(function(x){return '<li><span class="tpl">'+(x[0]||'추천')+'</span>'+esc(x[1].split('{t}').join(q))+'</li>'}).join('')+'</ul>';
      if(actCell[k])h+='<div class="rel"><b>과목 활동</b>'+actCell[k].slice(0,2).map(function(r){return esc(r.a)+' (<a href="#'+r.s.id+'">'+esc(r.s.name)+'</a>)'}).join(' · ')+'</div>';
      if(byCell[k])h+='<div class="stds"><b>성취기준</b> '+byCell[k].slice(0,3).map(function(r){return fullChip(r.x[0])}).join('')+'</div>';
      td.innerHTML=h+extra(k);
    });
    var sec=document.getElementById('std-section');
    var nd=stds.filter(function(r){return r.d}).length;
    note.textContent='‘'+q+'’'+(f?' ('+f+')':'')+'에 맞춰 칸마다 '+(f?f+' 관점의':'교과별 관점의')+' 활동을 추천했습니다. '+(rel.length?'연관어 '+rel.slice(0,8).join('·')+(rel.length>8?' 등':'')+'도 함께 찾았습니다. ':'')+(stds.length?'관련 성취기준 '+stds.length+'개'+(nd?'(주제어 직접 포함 '+nd+'개)':'(주제어가 직접 들어간 것은 없어 연관어로 찾음)')+'와 과목 활동 '+acts.length+'개를 관련도 순으로 표시했습니다. 성취기준은 주된 칸에 놓았습니다.':'관련 성취기준은 찾지 못했습니다. 더 짧거나 다른 낱말로 찾아보세요.');
    if(stds.length){
      sec.hidden=false;document.getElementById('std-title').textContent='‘'+q+'’ 관련 성취기준';
      document.getElementById('std-body').innerHTML=stds.slice(0,40).map(function(r){var s=r.x;
        return '<tr><td class="c">['+esc(s[0])+']</td><td><a class="subj" href="#'+r.s.id+'">'+esc(r.s.name)+'</a>'+esc(s[1])+'</td><td class="k">'+s[2].map(function(c,i){
          return '<button type="button" class="std-cell'+(i===0?' main':'')+'" data-cells="'+c+'">'+c+'<span>'+esc(DATA.names[c])+'</span></button>'}).join('')+'</td></tr>'}).join('');
    } else sec.hidden=true;
  }
  // 칸 상세: 수업 참여 · 주제탐구 예시 · 학교생활기록부 기재 예시
  var curView=null, dlg=document.getElementById('cell-dlg');
  function extra(k){var p=DATA.detail[k].part;
    return (p.length?'<div class="part"><b>수업 참여</b> '+esc(p[0])+'</div>':'')+'<button type="button" class="more" data-cell="'+k+'" aria-haspopup="dialog">탐구 예시 · 기재 예시</button>'}
  function openDetail(k){
    var d=DATA.detail[k], kn=DATA.knowledge.filter(function(x){return x[0]===k[0]})[0], pr=DATA.processes.filter(function(x){return x[0]===k[1]})[0];
    document.getElementById('dlg-code').textContent=k;
    document.getElementById('dlg-title').textContent=DATA.names[k];
    document.getElementById('dlg-sub').textContent=kn[1]+'('+kn[3]+') × '+pr[1]+'('+pr[4]+')';
    var h='';
    if(d.part.length) h+='<div class="callout"><b>기초 단계도 중요한 수업 참여입니다.</b> '+pr[1]+' 단계의 활동은 결과물보다 참여 과정(질문하기, 자기 말로 설명하기, 정확히 기록하기, 모둠 역할 수행)이 학생의 배움을 보여 줍니다. 수업 중 이렇게 참여하게 해 보세요.<ul>'+d.part.map(function(x){return '<li>'+esc(x)+'</li>'}).join('')+'</ul></div>';
    var sv=curView&&curView.standards?curView:null, acts=sv&&sv.cells[k]?sv.cells[k].acts:[];
    if(acts.length) h+='<h3>'+esc(sv.name)+' 활동<small>이 칸에 맞춘 과목 활동</small></h3><ul>'+acts.map(function(a){return '<li>'+esc(a[0])+a[1].map(function(c){return chip(c,'')}).join('')+'</li>'}).join('')+'</ul>';
    h+='<h3>주제탐구 활동 예시<small>탐구 질문 → 과정 → 산출물</small></h3>'+d.ex.map(function(e){
      return '<div class="ex"><h4>'+esc(e.t)+'</h4><p class="q">'+esc(e.q)+'</p><ol>'+e.s.map(function(x){return '<li>'+esc(x)+'</li>'}).join('')+'</ol><p class="o">산출물: '+esc(e.o)+'</p></div>'}).join('');
    var recs=acts.slice(0,2).map(function(a){return {by:sv.name+' · '+a[0],t:d.tpl.split('{s}').join(sv.name).split('{a}').join(a[0])}});
    recs=recs.concat(d.rec.map(function(t){return {by:'과목 공통 예시',t:t}}));
    h+='<h3>학교생활기록부 기재 예시<small>과목별 세부능력 및 특기사항</small></h3>'+recs.map(function(r){
      return '<div class="rec"><p><span class="by">'+esc(r.by)+'</span>'+esc(r.t)+'</p><button type="button" class="copy" data-t="'+esc(r.t)+'">복사</button></div>'}).join('');
    h+='<p class="dlg-note">기재 예시는 문장 틀입니다. 학생이 실제로 한 활동과 교사가 관찰한 모습으로 바꿔 쓰고, 기재 금지·유의 사항은 해당 학년도 「학교생활기록부 기재요령」을 따르세요.</p>';
    document.getElementById('dlg-body').innerHTML=h;hideTip();
    if(dlg.showModal){if(!dlg.open)dlg.showModal();}else dlg.setAttribute('open','');
    document.getElementById('dlg-body').scrollTop=0;dlg.scrollTop=0;
  }
  function closeDetail(){if(dlg.close)dlg.close();else dlg.removeAttribute('open')}
  document.getElementById('dlg-x').addEventListener('click',closeDetail);
  dlg.addEventListener('click',function(e){
    if(e.target===dlg){closeDetail();return;}
    var c=e.target.closest('.copy');if(c){var t=c.dataset.t;
      try{navigator.clipboard.writeText(t).then(function(){c.textContent='복사됨'},function(){c.textContent='복사 실패'})}catch(err){c.textContent='복사 실패'}}
  });
  function render(){
    var hh=(location.hash||'').slice(1);if(hh.indexOf('q=')===0){renderTopic(hh);return;}
    var id=(location.hash||'').slice(1); var v=views.filter(function(x){return x.id===id})[0]||views[0];curView=v;
    cur=v.area?ROW[v.area]:null;buildPanel();
    views.forEach(function(x){btn[x.id].setAttribute('aria-pressed',x===v?'true':'false')});
    clearMarks();
    document.body.className=AREA[v.area]?'a-'+AREA[v.area]:'';
    var byCell={};
    if(v.standards){v.standards.forEach(function(s){s[2].forEach(function(c,i){(byCell[c]=byCell[c]||[]).push({code:s[0],main:i===0})})});}
    Object.keys(DATA.names).forEach(function(k){
      var td=document.getElementById('c-'+k), cell=v.standards?v.cells[k]:DATA.common[k];
      var h='<span class="code">'+k+'</span><ul>'+cell.acts.map(function(a){
        return '<li>'+esc(a[0])+a[1].map(function(c){return chip(c,'')}).join('')+'</li>'}).join('')+'</ul>';
      if(!v.standards) h+='<div class="out"><b>산출물</b> '+esc(cell.out)+'</div>';
      else if(byCell[k]) h+='<div class="stds"><b>성취기준</b> '+byCell[k].map(function(x){return chip(x.code,x.main?' main':'')}).join('')+'</div>';
      td.innerHTML=h+extra(k);
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
    var m=e.target.closest('.more');if(m){openDetail(m.dataset.cell);return;}
    var td=e.target.closest('.mx tbody td');if(td&&!e.target.closest('a,button')&&!(window.getSelection&&String(window.getSelection()).length)){openDetail(td.id.slice(2));return;}
    var b=e.target.closest('.std-cell');if(b){mark([b.dataset.cells]);return;}
    var p=e.target.closest('.path');if(p){var on=p.getAttribute('aria-pressed')!=='true';clearMarks();
      if(on){mark(p.dataset.cells.split(' '));p.setAttribute('aria-pressed','true');}}
  });
  // 제목: 과목·표시를 지우고 처음 화면(전 과목 공통)으로
  document.getElementById('home').addEventListener('click',function(e){e.preventDefault();hideTip();
    if(location.hash)history.pushState(null,'',location.pathname+location.search);render();
    window.scrollTo({top:0,behavior:'smooth'});});
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
 *[f'| {g} | ' + ' · '.join(f'[{s["name"]}](subjects/{s["id"]}.md)' for s in SUBJECTS if s['group'] == g) + ' |' for g in GROUPS],
 '| 이 문서 안 | [두 축](#두-축) · [전 과목 공통 매트릭스](#전-과목-공통-매트릭스) · [탐구 경로 예시](#탐구-경로-예시) · [활용 안내](#활용-안내) |', '']

r = ['# 블룸의 개정 교육목표 분류로 보는 교과탐구활동 추천 매트릭스', '',
     'Anderson & Krathwohl(2001)의 개정 블룸 분류에서 **지식 차원(4)** × **인지 과정 차원(6)** 을 교차한 24칸에 탐구활동을 추천합니다. **2022 개정 교육과정** 고1 공통과목 14개(과학탐구실험 포함)와 2·3학년 일반선택·진로선택·융합선택 과목은 성취기준을 칸에 배치하고 과목별 활동을 따로 정리했습니다.', ''] + LINKS
r += ['## 두 축', '', '| 인지 과정 | 뜻 | 하위 과정 |', '|---|---|---|']
for c, ko, en, d, v in PROCESSES: r.append(f'| {c}. {ko} ({en}) | {d} | {v} |')
r += ['', '| 지식 차원 | 하위 유형 |', '|---|---|']
for c, ko, en, d in KNOWLEDGE: r.append(f'| {c}. {ko} ({en}) | {d} |')
r += ['', '## 과목별 매트릭스', '', '| 구분 | 과목 | 성취기준 수 | 성취기준이 가장 많이 모인 칸 |', '|---|---|---|---|']
for s in SUBJECTS:
    cnt = {}
    for _, _, cells in s['standards']: cnt[cells[0]] = cnt.get(cells[0], 0) + 1
    top = sorted(cnt.items(), key=lambda x: -x[1])[:2]
    r.append(f'| {s["group"]} | [{s["name"]}](subjects/{s["id"]}.md) | {len(s["standards"])} | ' + ', '.join(f'{k}({cell_name(k)}) {n}개' for k, n in top) + ' |')
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
 '- 성취기준: 교육부 고시 제2022-33호 2022 개정 교육과정. 공개 정리 자료에서 옮긴 뒤 과목마다 다른 공개 자료와 문장을 대조했지만(2026-10-29), [국가교육과정정보센터(NCIC)](https://www.ncic.re.kr) 원문과 다시 확인해 사용하세요. 일반선택 중 원문을 구하지 못한 현대사회와 윤리, 영어 진로선택 4과목(영어 발표와 토론·심화 영어·심화 영어 독해와 작문·직무 영어), 융합선택 4과목(실생활 영어 회화·미디어 영어·역사로 탐구하는 현대 세계·윤리문제 탐구)은 아직 넣지 않았습니다.',
 '- 칸 배치는 성취기준의 동사(인지 과정)와 목적어(지식 차원)를 기준으로 한 예시이며 교사 판단에 따라 바꿀 수 있습니다.',
 '- 내용은 `tools/data.py`(공통)와 `tools/subjects.py`(고1 공통), `tools/subjects_common2.py`(고1 2학기·과학탐구실험), `tools/subjects_general.py`(일반선택), `tools/subjects_career.py`(진로선택), `tools/subjects_convergence.py`(융합선택)에 있습니다. 고친 뒤 `cd tools && python3 gen.py`를 실행하면 `index.html`, `README.md`, `subjects/*.md`가 다시 만들어집니다.', '',
 'Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A Taxonomy for Learning, Teaching, and Assessing: A Revision of Bloom’s Taxonomy of Educational Objectives.* Longman.', '']
open(os.path.join(ROOT, 'README.md'), 'w').write('\n'.join(r))

os.makedirs(os.path.join(ROOT, 'subjects'), exist_ok=True)
for s in SUBJECTS:
    m = [f'# {s["name"]} 탐구활동 추천 매트릭스', '',
         f'2022 개정 교육과정 {s["name"]} 성취기준 {len(s["standards"])}개를 개정 블룸 분류 칸에 배치하고, 칸마다 과목에 맞춘 탐구활동을 정리했습니다. [전체 README로 돌아가기](../README.md)', '',
         '## 성취기준 배치', '', '주된 칸은 굵게 표시했습니다.', '', '| 코드 | 성취기준 | 칸 |', '|---|---|---|']
    for c, t, cells in s['standards']:
        m.append(f'| [{code(s, c)}] | {t} | ' + ', '.join((f'**{k}** {cell_name(k)}' if i == 0 else f'{k} {cell_name(k)}') for i, k in enumerate(cells)) + ' |')
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
