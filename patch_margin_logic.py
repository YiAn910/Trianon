#!/usr/bin/env python3

def must_replace(code, old, new, tag):
    n = code.count(old)
    assert n == 1, f"[{tag}] 锚点命中 {n} 处（应为 1），停止。"
    return code.replace(old, new)

# ---------- 1. JS: 空值锁定 22px，有值才撑开 ----------
p_js = 'src/rococo_v1.js'
s_js = open(p_js, encoding='utf-8').read()

# 匹配之前注入的旧 _sync 逻辑
old_sync = "const _sync=()=>{ci.style.height='auto';ci.style.height=Math.min(Math.max(ci.scrollHeight,22),120)+'px'};"
new_sync = "const _sync=()=>{if(!ci.value.trim()){ci.style.height='22px';return;}ci.style.height='auto';ci.style.height=Math.min(Math.max(ci.scrollHeight,22),120)+'px'};"

if old_sync in s_js:
    s_js = s_js.replace(old_sync, new_sync)
    print("JS: 成功更新 _sync 逻辑（空态 22px 锁定） ✓")
elif new_sync in s_js:
    print("JS: _sync 逻辑已是新版，跳过 ✓")
else:
    print("警告: 未匹配到旧 _sync 逻辑，请检查")

open(p_js, 'w', encoding='utf-8').write(s_js)

# ---------- 2. CSS: 给 .ci 加 margin-bottom: 40px ----------
p_css = 'src/rococo_v1.css'
s_css = open(p_css, encoding='utf-8').read()

# 定位当前行的末尾
old_ci_tail = "line-height:1.5;display:block;padding-top:2px}"
new_ci_tail = "line-height:1.5;display:block;padding-top:2px;margin-bottom:40px}"

if old_ci_tail in s_css:
    s_css = must_replace(s_css, old_ci_tail, new_ci_tail, 'rococo_v1.css margin-bottom')
    print("CSS: 成功为 .ci 添加 margin-bottom:40px ✓")
elif "margin-bottom:40px}" in s_css:
    print("CSS: .ci 已有 margin-bottom:40px，跳过 ✓")
else:
    print("警告: 未匹配到 .ci 的末尾，请检查")

open(p_css, 'w', encoding='utf-8').write(s_css)
print("=== 完美！终极方案执行完毕 ===")
