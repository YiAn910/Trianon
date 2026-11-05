#!/usr/bin/env python3
"""Inline markdown-it + highlight.js into rococo_v1.js/.css.
v2: brace check = pure-addition delta; optional node --check; dry-run default.
"""
import os, sys, shutil, subprocess, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
JS_PATH  = os.path.join(ROOT, 'src', 'rococo_v1.js')
CSS_PATH = os.path.join(ROOT, 'src', 'rococo_v1.css')
VENDOR   = os.path.join(ROOT, 'src', 'vendor')
APPLY = '--apply' in sys.argv

def read(p):
    with open(p, 'r', encoding='utf-8') as f: return f.read()
def log(m): print(m, flush=True)
def die(m):
    print('[ABORT] ' + m, file=sys.stderr, flush=True); sys.exit(1)

# 1. vendor
for fn in ['markdown-it.min.js', 'highlight.min.js', 'github.min.css']:
    p = os.path.join(VENDOR, fn)
    if not os.path.exists(p): die('missing vendor: ' + p)
    log('[vendor] %-22s %d bytes' % (fn, os.path.getsize(p)))
mdit = read(os.path.join(VENDOR, 'markdown-it.min.js'))
hljs = read(os.path.join(VENDOR, 'highlight.min.js'))
hlcss = read(os.path.join(VENDOR, 'github.min.css'))

# 2. source
js  = read(JS_PATH)
css = read(CSS_PATH)
log('[src] rococo_v1.js: %d bytes, rococo_v1.css: %d bytes' % (len(js), len(css)))

# 3. idempotency
MB = '/* MD-INLINE-BEGIN */'
in_js, in_css = (MB in js), (MB in css)
if in_js and in_css:
    log('[skip] already patched (both js & css have MD-INLINE-BEGIN)'); sys.exit(0)
if in_js or in_css:
    die('inconsistent state: js=%s css=%s' % (in_js, in_css))

# 4. anchors
if not js.rstrip().endswith('})();'):
    die('rococo_v1.js does not end with })();  tail=%r' % js[-80:])
cur_ref = js.count('window.__trianonRenderMD')
if cur_ref < 1: die('rococo_v1.js missing window.__trianonRenderMD refs')
log('[check] window.__trianonRenderMD refs in js = %d' % cur_ref)

# 5. escape </script>
mdit_e = mdit.replace('</script>', '<\\/script>')
hljs_e = hljs.replace('</script>', '<\\/script>')
if mdit.count('</script>'): log('[escape] markdown-it: %d escaped' % mdit.count('</script>'))
if hljs.count('</script>'): log('[escape] highlight.js: %d escaped' % hljs.count('</script>'))

# 6. render def
render_def = r'''
/* [MD-RENDER] window.__trianonRenderMD using inlined markdown-it + hljs */
(function(){
  if (typeof window.__trianonRenderMD === 'function') return;
  var mdit = window.markdownit, hl = window.hljs;
  if (!mdit) { console.warn('[MD] markdown-it not loaded'); return; }
  var md = mdit({
    html: false, linkify: true, breaks: true, typographer: false,
    highlight: function(str, lang){
      if (hl && lang && hl.getLanguage(lang)) {
        try { return '<pre class="hljs"><code>' + hl.highlight(str, {language: lang, ignoreIllegals: true}).value + '</code></pre>'; } catch(e) {}
      }
      return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
    }
  });
  window.__trianonRenderMD = function(raw){
    if (typeof raw !== 'string' || raw === '') return null;
    try { return md.render(raw); } catch(e) { console.warn('[MD] render error', e); return null; }
  };
})();
'''

# 7. append blocks
js_append = ('\n' + MB + '\n'
    + ';/* vendor: markdown-it 14.1.0 (MIT) */\n' + mdit_e + '\n'
    + ';/* vendor: highlight.js 11.9.0 (BSD-3-Clause) */\n' + hljs_e + '\n'
    + render_def
    + '/* MD-INLINE-END */\n')

css_append = ('\n' + MB + '\n' + hlcss + '\n' + r'''
/* ---- AI bubble Markdown typography (rococo) ---- */
.real-bubble.a p { margin: 0 0 8px 0; }
.real-bubble.a p:last-child { margin-bottom: 0; }
.real-bubble.a h1, .real-bubble.a h2, .real-bubble.a h3, .real-bubble.a h4 { margin: 12px 0 6px 0; font-weight: 600; line-height: 1.3; }
.real-bubble.a ul, .real-bubble.a ol { margin: 8px 0; padding-left: 22px; }
.real-bubble.a li { margin: 2px 0; }
.real-bubble.a blockquote { border-left: 3px solid #C5D0E5; margin: 8px 0; padding-left: 10px; color: #667; }
.real-bubble.a hr { border: none; border-top: 1px solid #E1E6F0; margin: 12px 0; }
.real-bubble.a a { color: #4A6FB5; text-decoration: none; border-bottom: 1px solid rgba(74,111,181,.35); }
.real-bubble.a :not(pre) > code { font-family: 'SF Mono','Consolas','Monaco',monospace; font-size: 13px; background: #F4F6F9; padding: 2px 5px; border-radius: 4px; color: #D14; }
.real-bubble.a pre { background: #F4F6F9; padding: 12px; border-radius: 6px; overflow-x: auto; border: 1px solid #E1E6F0; margin: 10px 0; }
.real-bubble.a pre code { font-family: 'SF Mono','Consolas','Monaco',monospace; font-size: 13px; background: transparent; padding: 0; }
.real-bubble.a table { border-collapse: collapse; margin: 8px 0; font-size: 13.5px; }
.real-bubble.a th, .real-bubble.a td { border: 1px solid #E1E6F0; padding: 6px 10px; }
.real-bubble.a th { background: #F4F6F9; font-weight: 600; }
/* MD-INLINE-END */
''')

# 8. v2 builder guard
V2_TARGETS = [
    "const sendNow=txt=>{txt=(txt||ci.value||'').trim()||window.__rkPrompt;if(busy())return;",
    "const busy=()=>running&&view==='live'&&!(tt>=T.END);",
    "const streaming=(t>=T.u&&t<T.sl+.2)||(t>=T.cp1&&t<T.q+.2)||(t>=T.qc1-.05&&t<T.c6z+.3);",
    "const waiting=(t>=T.sl+.25&&t<T.pr+.1)||(t>=T.q+.25&&t<T.sel+.1);",
    "const decideA=v=>{if(!running",
    "const decideQ=k=>{if(!running",
    "const reset=()=>{running=false;",
    "if(has('play'))setTimeout(play,500)",
    "window.__rk={get T(){return T},",
    "const dt=Math.max(0,Math.min(.1,t-lastT));sc+=",
    "const dtc=Math.max(0,Math.min(.1,t-lastT))",
    "window.__playGo=play;",
    "setClock(cvBusy,cvWait,t);",
    "window.__demoXY=()=>",
    "const mcM=$('mcM');",
]
for t in V2_TARGETS:
    if t in js_append: die('append contains v2 target: ' + t[:60])
log('[check] js_append has no v2 target (ok, %d checked)' % len(V2_TARGETS))

# 9. compose
new_js  = js  + js_append
new_css = css + css_append

# 10. verify
exp = cur_ref + render_def.count('window.__trianonRenderMD')
if new_js.count('window.__trianonRenderMD') != exp:
    die('renderMD count: expected %d, got %d' % (exp, new_js.count('window.__trianonRenderMD')))
if 'window.markdownit' not in new_js: die('window.markdownit missing')
if 'window.hljs' not in new_js:       die('window.hljs missing')
old_s = js.count('</script>'); new_s = new_js.count('</script>')
log('[check] </script> in js: %d -> %d' % (old_s, new_s))
if new_s > old_s: die('introduced %d new </script>' % (new_s - old_s))

# ---- brace: pure-addition delta (naive balance unreliable for minified JS) ----
def braces(s): return s.count('{'), s.count('}')
jb_old, jb_app, jb_new = braces(js), braces(js_append), braces(new_js)
cb_old, cb_app, cb_new = braces(css), braces(css_append), braces(new_css)
log('[check] js  old: {=%d }=%d  (delta=%d)' % (jb_old[0], jb_old[1], jb_old[0]-jb_old[1]))
log('[check] js  app: {=%d }=%d  (delta=%d)' % (jb_app[0], jb_app[1], jb_app[0]-jb_app[1]))
log('[check] js  new: {=%d }=%d  (delta=%d)' % (jb_new[0], jb_new[1], jb_new[0]-jb_new[1]))
log('[check] css old: {=%d }=%d' % cb_old)
log('[check] css app: {=%d }=%d' % cb_app)
log('[check] css new: {=%d }=%d' % cb_new)
if (jb_new[0]-jb_old[0], jb_new[1]-jb_old[1]) != jb_app:
    die('js brace delta mismatch (append content corrupted)')
if (cb_new[0]-cb_old[0], cb_new[1]-cb_old[1]) != cb_app:
    die('css brace delta mismatch (append content corrupted)')
log('[check] brace deltas match (no chars lost)')

# ---- optional node --check ----
if shutil.which('node'):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
        tf.write(new_js); tname = tf.name
    try:
        r = subprocess.run(['node', '--check', tname], capture_output=True, text=True)
        if r.returncode != 0:
            die('node --check FAILED:\n' + (r.stderr or r.stdout)[:2000])
        log('[check] node --check: PASS')
    finally:
        os.unlink(tname)
else:
    log('[check] node not found, syntax check skipped (browser Console will show errors)')

log('[size] js:  %d -> %d (+%d)' % (len(js),  len(new_js),  len(new_js)-len(js)))
log('[size] css: %d -> %d (+%d)' % (len(css), len(new_css), len(new_css)-len(css)))

# 11. dry-run
if not APPLY:
    log('')
    log('=== DRY RUN (no files written) ===')
    log('Re-run with: python3 patch_markdown_inline.py --apply')
    log('')
    log('--- js_append first 400 chars ---')
    log(js_append[:400])
    log('...')
    log('--- js_append last 700 chars ---')
    log(js_append[-700:])
    log('')
    log('--- css_append first 300 chars ---')
    log(css_append[:300])
    sys.exit(0)

# 12. backup + atomic write
def atomic(path, content, suffix):
    bak = path + suffix
    if not os.path.exists(bak):
        shutil.copy(path, bak); log('[backup] ' + bak)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f: f.write(content)
    with open(tmp, 'r', encoding='utf-8') as f: back = f.read()
    if back != content: die('readback mismatch: ' + tmp)
    os.replace(tmp, path)
    log('[write] %s (%d bytes)' % (path, os.path.getsize(path)))

atomic(JS_PATH,  new_js,  '.bak_md_inline_pre')
atomic(CSS_PATH, new_css, '.bak_md_inline_pre')

log('')
log('=== DONE ===')
log('Next: python build.py')
log('Then: http://localhost:8088/dist/trianon.html')
log('Rollback: cp src/rococo_v1.js.bak_md_inline_pre src/rococo_v1.js && cp src/rococo_v1.css.bak_md_inline_pre src/rococo_v1.css && python build.py')
