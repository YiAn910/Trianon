#!/usr/bin/env python3
import os, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, 'src')

def bak(path):
    b = path + '.bak_textarea'
    if not os.path.exists(b):
        shutil.copy2(path, b)
        print('backup ->', os.path.basename(b))
    return b

def must(s, old, tag):
    n = s.count(old)
    assert n == 1, ('ANCHOR FAIL', tag, old[:80], 'count=', n)
    print('anchor OK ->', tag)

# 1) build_rococo_v1.py: input -> textarea
p = os.path.join(SRC, 'build_rococo_v1.py'); bak(p)
s = open(p, encoding='utf-8').read()
o = '<input class="ci" id="ci" type="text" autocomplete="off" spellcheck="false" aria-label="说一句话">'
n = '<textarea class="ci" id="ci" rows="1" autocomplete="off" spellcheck="false" aria-label="说一句话"></textarea>'
must(s, o, 'build_rococo_v1.py input'); open(p, 'w', encoding='utf-8').write(s.replace(o, n))

# 2) rococo_v1.css: layout
p = os.path.join(SRC, 'rococo_v1.css'); bak(p)
s = open(p, encoding='utf-8').read()
o = ('.field .ph{position:relative;cursor:text}\n'
     '.field .ph .ci{position:absolute;left:0;top:0;width:100%;height:100%;border:0;outline:0;background:none;padding:0;margin:0;\n'
     ' font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;padding-right:92px;box-sizing:border-box}')
n = ('.field .ph{position:relative;cursor:text;min-height:30px}\n'
     '.field .ph .ci{position:absolute;left:0;top:0;width:100%;height:auto;min-height:30px;max-height:120px;overflow-y:auto;resize:none;border:0;outline:0;background:none;padding:0;margin:0;\n'
     ' font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;padding-right:92px;box-sizing:border-box;line-height:1.5;display:block}')
must(s, o, 'rococo_v1.css .field .ph .ci'); open(p, 'w', encoding='utf-8').write(s.replace(o, n))

# 3) rococo_v1.js: auto-height sync
p = os.path.join(SRC, 'rococo_v1.js'); bak(p)
s = open(p, encoding='utf-8').read()
o = "ci.addEventListener('input',()=>field.classList.toggle('has',!!ci.value));"
n = o + ("\n(()=>{const _ph=field.querySelector('.ph');if(!_ph||ci.tagName!=='TEXTAREA')return;"
         "const _sync=()=>{_ph.style.height=Math.min(Math.max(ci.scrollHeight,30),120)+'px'};"
         "ci.addEventListener('input',_sync);window.addEventListener('resize',_sync);_sync()})();")
must(s, o, 'rococo_v1.js ci input listener'); open(p, 'w', encoding='utf-8').write(s.replace(o, n))

print('ALL PATCHED OK')
