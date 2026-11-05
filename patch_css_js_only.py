#!/usr/bin/env python3

def must_replace(code, old, new, tag):
    n = code.count(old)
    assert n == 1, f"锚点失败 [{tag}]: 预期 1 处，实际发现 {n} 处。"
    return code.replace(old, new)

# 1. 修复 rococo_v1.css
p_css = 'src/rococo_v1.css'
s = open(p_css, encoding='utf-8').read()

old_css_block = """.field .ph{position:relative;cursor:text}
.field .ph .ci{position:absolute;left:0;top:0;width:100%;height:100%;border:0;outline:0;background:none;padding:0;margin:0;
 font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;padding-right:92px;box-sizing:border-box}
.field .ph em,.field .ph .pht{transition:opacity .2s}
.field.has .ph em,.field.has .ph .pht{opacity:0}"""

new_css_block = """.field .ph{position:relative;cursor:text;padding:4px 0}
.field .ph-txt{position:absolute;left:0;top:6px;pointer-events:none;transition:opacity .2s}
.field .ph .ci{position:relative;width:100%;height:auto;min-height:22px;max-height:120px;overflow-y:auto;resize:none;border:0;outline:0;background:none;padding:0;margin:0;
 font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;padding-right:92px;box-sizing:border-box;line-height:1.5;display:block}
.field.has .ph-txt{opacity:0}"""

s = must_replace(s, old_css_block, new_css_block, 'rococo_v1.css')
open(p_css, 'w', encoding='utf-8').write(s)
print("1/2 CSS 布局替换成功。")

# 2. 修复 rococo_v1.js
p_js = 'src/rococo_v1.js'
s = open(p_js, encoding='utf-8').read()
old_js = "ci.addEventListener('input',()=>field.classList.toggle('has',!!ci.value));"
new_js = "ci.addEventListener('input',()=>field.classList.toggle('has',!!ci.value));\n(()=>{if(ci.tagName!=='TEXTAREA')return;const _sync=()=>{ci.style.height='auto';ci.style.height=Math.min(ci.scrollHeight,120)+'px'};ci.addEventListener('input',_sync);window.addEventListener('resize',_sync);_sync()})();"
s = must_replace(s, old_js, new_js, 'rococo_v1.js')
open(p_js, 'w', encoding='utf-8').write(s)
print("2/2 JS 自适应替换成功。")

print("=== 完美！严格校验通过，已写入 ===")
