#!/usr/bin/env python3
import os

# 1. JS: 移除上次加的自适应高度逻辑，恢复最干净的状态
p_js = 'src/rococo_v1.js'
s_js = open(p_js, encoding='utf-8').read()
old_js = "ci.addEventListener('input',()=>field.classList.toggle('has',!!ci.value));\n(()=>{const _ph=field.querySelector('.ph');if(!_ph||ci.tagName!=='TEXTAREA')return;const _sync=()=>{ci.style.height='auto';const _h=Math.min(Math.max(ci.scrollHeight,30),120);ci.style.height=_h+'px';_ph.style.height=_h+'px'};ci.addEventListener('input',_sync);ci.addEventListener('change',_sync);ci.addEventListener('paste',()=>setTimeout(_sync,10));ci.addEventListener('compositionend',_sync);window.addEventListener('resize',_sync);_sync()})();"
new_js = "ci.addEventListener('input',()=>field.classList.toggle('has',!!ci.value));"
if s_js.count(old_js) == 1:
    s_js = s_js.replace(old_js, new_js)
    open(p_js, 'w', encoding='utf-8').write(s_js)
    print('patched JS restored OK')
else:
    print('警告: JS 锚点未找到（跳过）')

# 2. CSS: 让 textarea 回归文档流，占位符绝对定位浮在上方
p_css = 'src/rococo_v1.css'
s_css = open(p_css, encoding='utf-8').read()

old_css = ".field .ph{position:relative;cursor:text;min-height:30px}\n.field .ph .ci{position:absolute;left:0;top:0;width:100%;height:100%;min-height:30px;max-height:120px;overflow-y:auto;resize:none;border:0;outline:0;background:none;padding:4px 92px 4px 0;margin:0;\n font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;box-sizing:border-box;line-height:1.5;display:block}"

new_css = ".field .ph{position:relative;cursor:text;min-height:30px}\n.field .ph em,.field .ph .pht{position:absolute;left:0;top:4px;pointer-events:none}\n.field .ph .ci{position:relative;width:100%;height:auto;min-height:30px;max-height:120px;overflow-y:auto;resize:none;border:0;outline:0;background:none;padding:4px 92px 4px 0;margin:0;\n font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;box-sizing:border-box;line-height:1.5;display:block}"

if s_css.count(old_css) == 1:
    s_css = s_css.replace(old_css, new_css)
    open(p_css, 'w', encoding='utf-8').write(s_css)
    print('patched CSS OK')
else:
    # 尝试兼容换行符差异
    old_css2 = old_css.replace('\n', '\r\n')
    if s_css.count(old_css2) == 1:
        s_css = s_css.replace(old_css2, new_css)
        open(p_css, 'w', encoding='utf-8').write(s_css)
        print('patched CSS OK (CRLF)')
    else:
        print('错误: CSS 锚点未找到，请停止操作并反馈')
