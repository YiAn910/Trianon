#!/usr/bin/env python3

def must_replace(code, old, new, tag):
    n = code.count(old)
    assert n == 1, f"锚点失败 [{tag}]: 预期 1 处，实际发现 {n} 处。"
    return code.replace(old, new)

# 1. CSS: 调整占位符对齐，添加滚动条样式支持
p_css = 'src/rococo_v1.css'
s = open(p_css, encoding='utf-8').read()
old_css = ".field .ph-txt{position:absolute;left:0;top:6px;pointer-events:none;transition:opacity .2s}"
new_css = ".field .ph-txt{position:absolute;left:0;top:2px;pointer-events:none;transition:opacity .2s}"
s = must_replace(s, old_css, new_css, 'rococo_v1.css top')

# 确保 ci 的 padding-top 和 line-height 也是对齐的
old_ci = "font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;padding-right:92px;box-sizing:border-box;line-height:1.5;display:block}"
new_ci = "font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;padding-right:92px;box-sizing:border-box;line-height:1.5;display:block;padding-top:2px}"
s = must_replace(s, old_ci, new_ci, 'rococo_v1.css ci padding')
open(p_css, 'w', encoding='utf-8').write(s)
print("1/2 CSS 修改成功。")

# 2. JS: 强制用 JS 撑开 textarea，把按钮顶下去
p_js = 'src/rococo_v1.js'
s = open(p_js, encoding='utf-8').read()

# 我们直接替换上次刚加的自适应代码，加入 paste 和 change 事件，确保每次都算
old_js = "(()=>{if(ci.tagName!=='TEXTAREA')return;const _sync=()=>{ci.style.height='auto';ci.style.height=Math.min(ci.scrollHeight,120)+'px'};ci.addEventListener('input',_sync);window.addEventListener('resize',_sync);_sync()})();"
new_js = "(()=>{if(ci.tagName!=='TEXTAREA')return;const _sync=()=>{ci.style.height='auto';ci.style.height=Math.min(Math.max(ci.scrollHeight,22),120)+'px'};['input','change','paste','focus'].forEach(ev=>ci.addEventListener(ev,()=>setTimeout(_sync,10)));window.addEventListener('resize',_sync);_sync()})();"

s = must_replace(s, old_js, new_js, 'rococo_v1.js height sync')
open(p_js, 'w', encoding='utf-8').write(s)
print("2/2 JS 修改成功。")

print("=== 严格校验通过，已写入 ===")
