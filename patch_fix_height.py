#!/usr/bin/env python3
import os

# 1. JS: 每次输入强制重算并直接修改 ci 自身高度
p_js = 'src/rococo_v1.js'
s_js = open(p_js, encoding='utf-8').read()
old_js = "(()=>{const _ph=field.querySelector('.ph');if(!_ph||ci.tagName!=='TEXTAREA')return;const _sync=()=>{_ph.style.height=Math.min(Math.max(ci.scrollHeight,30),120)+'px'};ci.addEventListener('input',_sync);window.addEventListener('resize',_sync);_sync()})();"
new_js = "(()=>{const _ph=field.querySelector('.ph');if(!_ph||ci.tagName!=='TEXTAREA')return;const _sync=()=>{ci.style.height='auto';const _h=Math.min(Math.max(ci.scrollHeight,30),120);ci.style.height=_h+'px';_ph.style.height=_h+'px'};ci.addEventListener('input',_sync);ci.addEventListener('change',_sync);ci.addEventListener('paste',()=>setTimeout(_sync,10));ci.addEventListener('compositionend',_sync);window.addEventListener('resize',_sync);_sync()})();"
assert s_js.count(old_js) == 1, 'JS 锚点未找到'
s_js = s_js.replace(old_js, new_js)
open(p_js, 'w', encoding='utf-8').write(s_js)
print('patched JS OK')

# 2. CSS: 恢复高度为 100%，并加上下内边距让文字呼吸
p_css = 'src/rococo_v1.css'
s_css = open(p_css, encoding='utf-8').read()
old_css = ".field .ph .ci{position:absolute;left:0;top:0;width:100%;height:auto;min-height:30px;max-height:120px;overflow-y:auto;resize:none;border:0;outline:0;background:none;padding:0;margin:0;\n font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;padding-right:92px;box-sizing:border-box;line-height:1.5;display:block}"
new_css = ".field .ph .ci{position:absolute;left:0;top:0;width:100%;height:100%;min-height:30px;max-height:120px;overflow-y:auto;resize:none;border:0;outline:0;background:none;padding:4px 92px 4px 0;margin:0;\n font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;box-sizing:border-box;line-height:1.5;display:block}"
assert s_css.count(old_css) == 1, 'CSS 锚点未找到'
s_css = s_css.replace(old_css, new_css)
open(p_css, 'w', encoding='utf-8').write(s_css)
print('patched CSS OK')
