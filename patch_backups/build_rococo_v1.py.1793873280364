#!/usr/bin/env python3
"""Build rococo_v1.html: the merged, clickable Foggy-Blue (雾蓝拼贴) desktop prototype.
All approved states live in one page and one shared shell, wired together as real flows instead of separate forks of v8:
  empty page (v11) -> composer send / preset tag -> empty paper lifts away -> user bubble -> Kimi streams (v12 blossom, 落笔中)
  -> tool notes (tools_v2: reads gather) -> permission slip (approval_v2, waits for 允许 / 本会话都允许 / 拒绝)
  -> question card (approval_v2, waits for a choice) -> proof-sheet diff, shell typecheck, failing test, fix, pass -> summary bar.
  The dossier column (Plan / Changes / Context) follows the turn. Rail hourglass opens the sessions drawer (sessions_v2);
  a past session opens the completed v8 conversation; the bow ("新的对话") returns to the empty page; the composer model tag,
  popover and catalogue (sessions_v2) work everywhere.
Sources are read only. Pieces are taken from the existing build scripts at build time (their definition parts are exec'd,
never their write steps): build_v11.py (empty), build_v12.py (落笔中 label), build_sessions_v2.py (drawer + model layer, which
itself reuses build_v13.py), build_tools_v2.py (tool notes, proof sheets, shell receipts, summary), build_approval_v2.py
(slip, seal, stamp, question card, composer wait clock).
Class clash fixed: tools' proof sheet .pf* -> .prf* (sessions owns .pf project folders); approval's .seal -> .ap-seal (the
drawer envelope has an svg .seal). Every model label reads K3.1 Pro.
Hooks: #empty #chat (=#hist past conversation) #stream #tools #approval (=#pend) #q #qok #diff #fail #end #sessions #model #cat
#play (self-running demo) and #t=<sec> (freeze the turn).  window.__rk = engine (events(), T, start, reset, ...).
Demo cursor: window.__realMouse=true stops the demo cursor from synthesising pointer events
(the recorder moves the real mouse to window.__demoXY())."""
import os, re, json

HERE = './'
OUT = HERE + 'rococo_v1.html'
os.environ['KB_DIR'] = HERE.rstrip('/')

def defs(fname, marker, patch=None):
    src = open(HERE + fname, encoding='utf-8').read()
    assert src.count(marker) >= 1, (fname, marker)
    src = src.split(marker)[0]
    if patch:
        for a, z in patch:
            assert src.count(a) == 1, (fname, a[:60], src.count(a))
            src = src.replace(a, z)
    ns = {'__name__': 'defs_' + fname}
    exec(compile(src, fname + ':defs', 'exec'), ns)
    return ns

# ---------------------------------------------------------------- sources (definitions only)
V11 = defs('build_v11.py', "out = s[:s.find('<div class=\"scroll\">')]")
V12 = defs('build_v12.py', "sub1('<title>Kimi Code")
S2 = defs('build_sessions_v2.py', '# ---------- assemble', patch=[
    # the live conversation is the drawer's current slip; the approved v8 conversation is a finished session
    ("(P1, True, [('重构聊天工作台的流式渲染', '刚刚', 'cur'),", "(P1, True, [('新的对话', '刚刚', 'cur'),"),
    ("(P1, True, [('阶段 2 · 契约冻结与评审', '10/22'),", "(P1, True, [('重构聊天工作台的流式渲染', '10/25'), ('阶段 2 · 契约冻结与评审', '10/22'),"),
])
TV = defs('build_tools_v2.py', '# ---------------------------------------------------------------- model layer')
AP = defs('build_approval_v2.py', 'import json\npre =')

s = open(HERE + 'v8.html', encoding='utf-8').read()
def sub1(old, new):
    global s
    assert s.count(old) == 1, (old[:90], s.count(old))
    s = s.replace(old, new)

# ---------------------------------------------------------------- class clash fixes
def prf_html(x):   # tools proof sheet classes -> .prf*
    return re.sub(r'class="pf(-\w+)?"', lambda m: 'class="prf' + (m.group(1) or '') + '"', x)
def prf_css(x):
    return re.sub(r'\.pf(?=[-\s{:,.>)\[])', '.prf', x)
TV_CSS = prf_css(TV['CSS'])
assert '.prf-w{' in TV_CSS and '.prf{' in TV_CSS and '.pf-' not in TV_CSS
AP_CSS = AP['CSS'].replace('.seal{', '.ap-seal{').replace('.seal svg{', '.ap-seal svg{')
assert '.seal' not in AP_CSS.replace('.ap-seal', '')
AP_SLIP = AP['SLIP'].replace('<div class="seal" id="seal">', '<div class="ap-seal" id="seal">')
assert 'class="seal"' not in AP_SLIP
# approval DEFS also declares a gradient named apHg, which collides with the composer hourglass group; the halo it fed is not used here
AP_DEFS = AP['DEFS'].replace('<radialGradient id="apHg">', '<radialGradient id="apHgUnused">')

# v12: only the "Kimi 正在落笔…" label (the blossom and stop ring come from the tools/approval engines, identical artwork)
PEN_CSS = '<style id="v12pen">\n' + '\n'.join(m.group(0).strip() for m in re.finditer(r'[^{}]+\{[^}]*\}', V12['CSS']) if 'pen12' in m.group(0) or re.sub(r'/\*.*?\*/', '', m.group(0), flags=re.S).strip().startswith('.who{')) + '\n</style>\n'
assert '.pen12{' in PEN_CSS and '.who{position:relative}' in PEN_CSS
PEN = '<span class="pen12" id="pen12" aria-live="polite"><em>Kimi</em>正在落笔<i><b>·</b><b>·</b><b>·</b></i></span>'

# ---------------------------------------------------------------- the live turn (one Kimi turn on paper)
note, badge = TV['note'], TV['badge']
A1 = note('rkA1', 'edit', 5, 'StrReplaceFile', 'src/renderer/engine/adapter.ts', '0.3s', cls='ed',
          meta='<span class="n a">+3</span><span class="n d">−1</span>')
SUM = TV['SUM']
for a, z in [('<b>改动了 2 个文件</b><span class="n a">+18</span><span class="n d">−9</span>',
              '<b id="rkSumH">改动了 3 个文件</b><span class="n a" id="rkSumA">+21</span><span class="n d" id="rkSumD">−10</span>'),
             ('<div class="ts-f">',
              f'<div class="ts-r" id="rkSumR">{badge("edit", 4)}<span class="p"><i>src/renderer/engine/</i>adapter.ts</span><span class="ts-c">按 id 去重</span>'
              '<span class="n a">+3</span><span class="n d">−1</span></div><div class="ts-f">')]:
    assert SUM.count(a) == 1, a
    SUM = SUM.replace(a, z)

PROMPT0 = '流式回复每个 delta 都触发一次重排，长会话会卡。改成按帧批量提交，别让已完成的消息重复插入。'
LIVECOL = f'''<div class="dsep" id="rkSep"><span>今日 · 10月26日 · 夜</span></div>
      <div class="row out rk-u" id="rkU"><div class="b" id="rkUb">{PROMPT0}</div></div>
      <div class="row in tv-row ap-row rk-row" id="rkRow"><div class="col">
        <div class="who" id="rkWho">K I M I{PEN}</div>
        <div class="b tl" id="rkB1">先看一眼现在的提交路径。</div>
        {TV['GROUP']}
        <div class="b" id="rkB2">找到了两处：结束时整条 push，没按 id 去重；每个 delta 都直接 commit，再重排一次。先把去重补上：</div>
        {AP_SLIP}
        {A1}
        <div class="b" id="rkB3">去重补上了。动手合批之前，有个取舍想听你的：</div>
        {AP['QCARD']}
        <div class="b" id="rkB4">好，按帧批处理。改成先攒着，下一帧一次提交：</div>
        {prf_html(TV['E1'])}
        {prf_html(TV['E2'])}
        {TV['SH1']}
        {TV['SH2']}
        <div class="b" id="rkB5">有一条没过：结束事件在同一帧里又单独重排了一次。让它也走 flushFrame。</div>
        {prf_html(TV['E3'])}
        {TV['SH3']}
        <div class="b" id="rkB6">好了。完成的消息按 id 合并，不再整条重复插入；delta 按帧合批，一帧只重排一次，结束事件也并进同一帧；测试改了 1 条、补了 1 条，24 条全部通过。</div>
        {SUM}
      </div></div>'''
assert 'class="pf' not in LIVECOL

# ---------------------------------------------------------------- the past conversation (v8, finished)
th0 = s.index('<div class="scroll"><div class="thread">')
th1 = s.index('<div class="composer">')
hist = s[th0 + len('<div class="scroll"><div class="thread">'):th1]
hist = hist[:hist.rindex('</div></div>')]
for a, z in [('今日 · 10月25日 · 午后', '10月25日 · 午后'),
             ('<div class="tool run">', '<div class="tool">'),
             ('<span class="d">进行中</span>', '<span class="d">0.6s</span>'),
             ('<div class="row in"><div class="col"><div class="typing"><i></i><i></i><i></i></div></div></div>',
              '<div class="row in"><div class="col"><div class="b tl">补上了：结束时按 message id 合并，已完成的消息不再整条重复插入；流式测试也加了一条。</div></div></div>')]:
    assert hist.count(a) == 1, a
    hist = hist.replace(a, z)

HERO = V11['HERO']
a = '<div class="scroll empty"><div class="hall">'
assert HERO.count(a) == 1
HERO = HERO.replace(a, '<div class="scroll empty vw on" id="vEmpty"><div class="hall">')
VIEWS = (HERO.rstrip() + '\n    <div class="scroll chat vw" id="vLive"><div class="thread" id="thLive">\n      ' + LIVECOL +
         '\n    </div></div>\n    <div class="scroll chat vw" id="vHist"><div class="thread" id="thHist">' + hist + '</div></div>\n\n    ')
s = s[:th0] + VIEWS + s[th1:]

# ---------------------------------------------------------------- dossier: live (engine-driven) + past (v8 as approved)
d0 = s.index('<div class="dossier">'); d1 = s.index('</aside>', d0)
dos = s[d0:d1].rstrip()
assert dos.endswith('</div>')
dos_hist = dos.replace('<div class="dossier">', '<div class="dossier" id="dsHist" style="display:none">', 1).replace('<small>Kimi K2.5</small>', '<small>K3.1 Pro</small>')
CHECKSVG = TV['CHECK']
PLAN = ['读 stream.ts，找到提交入口', '完成的消息按 id 去重', 'delta 按帧合批，补测试', '类型检查与测试全绿']
plan_rows = ''.join(f'<div class="td todo rk-td"><span class="mk">◇</span><span class="tx">{p}</span>'
                    + (f'<span class="ap-wt" id="rkWt{k}"><em>attente</em><span>{"等待许可" if k == 1 else "等待回答"}</span></span>' if k in (1, 2) else '')
                    + '</div>' for k, p in enumerate(PLAN))
dos_live = f'''<div class="dossier" id="dsLive">
    <div class="sec"><h5><em>Plan</em>计 划<small id="rkPlanH">—</small></h5>
      <div class="tv-none rk-none" id="rkPlanNone">rien encore<span>尚无计划</span></div>
      {plan_rows}
    </div>
    <div class="orn"><span>✦</span></div>
    <div class="sec"><h5><em>Changes</em>改 动<small id="rkLeaves">no leaves</small></h5>
      <div class="tv-none" id="tvNone">rien encore<span>尚无改动</span></div>
      <div class="fx tv-fx" id="rkFxC"><span class="p"><em>src/renderer/engine/</em>adapter.ts</span><span class="n a">+3</span><span class="n d">−1</span></div>
      <div class="fx tv-fx" id="tvFxA"><span class="p"><em>src/renderer/</em>stream.ts</span><span class="n a tv-num" id="tvFxAa">+12</span><span class="n d tv-num" id="tvFxAd">−4</span></div>
      <div class="fx tv-fx" id="tvFxB"><span class="p"><em>tests/</em>stream.test.ts</span><span class="n a">+5</span><span class="n d">−3</span></div>
      <div class="tv-tot" id="tvTot">total <span class="n a" id="tvTa">+3</span><span class="n d" id="tvTd">−1</span></div>
    </div>
    <div class="orn"><span>✦</span></div>
    <div class="sec ctxp"><h5><em>Context</em>上 下 文<small id="rkCtxM">K3.1 Pro</small></h5>
      <div class="r1"><span class="pc" id="rkPc">6%</span><span class="of" id="rkOf">16k of 262k</span></div>
      <div class="gauge"><div class="tk"></div><div class="groove"><i id="rkGi" style="width:6%"></i></div><b id="rkGb" style="left:6%">✦</b></div>
    </div>
  </div>
  '''
s = s[:d0] + dos_live + dos_hist + '\n' + s[d1:]
sub1('<div class="cap">今 夜 卷 宗<b>流式渲染的重构</b></div>', '<div class="cap">今 夜 卷 宗<b id="rkCap">新的信笺</b></div>')

# ---------------------------------------------------------------- rail: hourglass wrapper + drawer keeps the rail open (as sessions_v2)
nav0 = s.index('<nav class="rail">'); nav1 = s.index('</nav>', nav0)
nav = s[nav0:nav1]
m = re.search(r'(<div class="it" style="--i:1">)(<img src="data:image/png;base64,[A-Za-z0-9+/=]+" alt="">)', nav)
assert m
nav = nav[:m.start()] + m.group(1) + '<b class="hgw">' + m.group(2) + '</b>' + S2['SAND'] + nav[m.end():]
s = s[:nav0] + nav + s[nav1:]
sub1("else{if(x>rail.getBoundingClientRect().right+36){",
     "else{if(x>(b.classList.contains('drw-open')?document.getElementById('drw').getBoundingClientRect().right:rail.getBoundingClientRect().right)+36){")
sub1("document.addEventListener('pointerleave',()=>{clearTimeout(tOpen);tOpen=0;if(open&&!tClose)",
     "document.addEventListener('pointerleave',()=>{clearTimeout(tOpen);tOpen=0;if(open&&!tClose&&!b.classList.contains('drw-open'))")

# ---------------------------------------------------------------- composer: a real line to write on, model tag, stop / wait clock
sub1('<div class="ph"><em>Écrivez-moi</em>说一句话⋯</div>',
     '<div class="ph"><div class="ph-txt"><em>Écrivez-moi</em><span class="pht">说一句话⋯</span></div>'
     '<textarea class="ci" id="ci" rows="1" autocomplete="off" spellcheck="false" aria-label="说一句话"></textarea></div>')
sub1('<div class="pill rb blue">@ 文件</div></div>', '<div class="pill rb blue">@ 文件</div>' + S2['CHIP'] + '</div>')
sub1('<span class="sl">Envoyer</span>', '<span class="sl s0">Envoyer</span><span class="sl s1">Stopper</span><span class="sl s2">Patience</span>' + AP['STOP'])
sub1('<div class="send">', '<div class="send" role="button" tabindex="0" aria-label="发送">')
# every model label reads K3.1 Pro (the hidden top bar too)
sub1('<div class="model">模型 <b>Kimi K2.5</b> ▾</div>', '<div class="model">模型 <b id="rkTopM">K3.1 Pro</b> ▾</div>')
sub1('<title>Kimi Code · 蓝雾厅 v8</title>', '<title>Kimi Code · 蓝雾厅 · 洛可可桌面端 rococo v1</title>')
sub1('<body>', '<body class="v-empty">')

# ---------------------------------------------------------------- own CSS
RK_CSS = open(HERE + 'rococo_v1.css', encoding='utf-8').read()
RK_JS = open(HERE + 'rococo_v1.js', encoding='utf-8').read()
CSS = (S2['CSS13'] + S2['CSS2'] + V11['CSS'] + PEN_CSS + TV_CSS + AP_CSS +
       '<style id="rococoV1">\n' + RK_CSS + '\n/* tools v2: the tag never runs under the bow / pen */\n.composer .field .bar .mchip{flex:none;margin-right:6px}\n</style>\n')
sub1('</head>', CSS + '</head>')

pre = ('<script>window.__rkCheck=' + json.dumps(CHECKSVG) + ';window.__rkCk=' + json.dumps(AP['CK']) + ';window.__rkX=' + json.dumps(AP['XX']) +
       ';window.__rkPrompt=' + json.dumps(PROMPT0) + ';</script>')
v11js = V11['JS']
for a, z in [("const go=()=>{if(RM.matches){still();return}const t0=performance.now();\n const loop=n=>{frame((n-t0)/1000);requestAnimationFrame(loop)};requestAnimationFrame(loop)};",
              "let t0=performance.now();const vE=document.getElementById('vEmpty');\n"
              "window.__v11restart=()=>{t0=performance.now();if(RM.matches)still();else frame(0)};\n"
              "const go=()=>{if(RM.matches){still();return}t0=performance.now();\n"
              " const loop=n=>{if(vE.classList.contains('on')||vE.classList.contains('out'))frame(Math.max(0,(n-t0)/1000));requestAnimationFrame(loop)};requestAnimationFrame(loop)};")]:
    assert v11js.count(a) == 1, a[:60]
    v11js = v11js.replace(a, z)
idx = s.rfind('</body>')
s = (s[:idx] + AP_DEFS + TV['DEFS'] + S2['DEFS'] + TV['FLOWER'] + S2['DRAWER'] + S2['POP'] + S2['MODAL'] +
     S2['JS'] + S2['JS2'] + v11js + pre + '<script>\n' + RK_JS + '\n</script>' + s[idx:])

# ---------------------------------------------------------------- sanity: duplicate ids
ids = re.findall(r'\sid="([^"]+)"', re.sub(r'<script>.*?</script>', '', s, flags=re.S))
dup = sorted({i for i in ids if ids.count(i) > 1} - {'tvPearl', 'tvSteel'})   # identical pin gradients repeated per proof sheet (as in tools_v2)
assert not dup, dup
open(OUT, 'w', encoding='utf-8').write(s)
print('wrote', OUT, len(s))
