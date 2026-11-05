#!/usr/bin/env python3
def must_replace(code, old, new, tag):
    n = code.count(old)
    assert n == 1, f"[{tag}] 锚点命中 {n} 处（应为 1），停止。"
    return code.replace(old, new)

# ---------- CSS：移除上次追加的强覆盖 ----------
p = 'src/rococo_v1.css'
s = open(p, encoding='utf-8').read()

BAD_TAIL = """.field{height:auto!important;}
.field .ph{position:relative;cursor:text;padding:0;display:block;}
.field .ph-txt{position:absolute;left:0;top:0;pointer-events:none;transition:opacity .2s;line-height:1.5}
.field .ph .ci{position:relative!important;display:block!important;width:100%;height:22px;min-height:22px;max-height:120px;overflow-y:auto;resize:none;border:0;outline:0;background:none;padding:0;padding-right:92px;margin:0;
 font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;box-sizing:border-box;line-height:1.5}
.field .bar{margin-top:10px!important;position:relative!important;}"""
if BAD_TAIL in s:
    s = s.replace(BAD_TAIL, '')
    print("CSS: 移除上次追加的强覆盖 ✓")
else:
    print("CSS: 未发现上次追加的强覆盖（可能没执行成功）")

# 顺便把之前可能把 top 写死的占位符修正一下
if ".field .ph-txt{position:absolute;left:0;top:2px;pointer-events:none;transition:opacity .2s}" not in s and ".field .ph-txt{position:absolute;left:0;top:6px;pointer-events:none;transition:opacity .2s}" in s:
    s = s.replace(".field .ph-txt{position:absolute;left:0;top:6px;pointer-events:none;transition:opacity .2s}", ".field .ph-txt{position:absolute;left:0;top:4px;pointer-events:none;transition:opacity .2s}")

open(p, 'w', encoding='utf-8').write(s)

# ---------- JS：无 _sync 才注入 ----------
p = 'src/rococo_v1.js'
s = open(p, encoding='utf-8').read()
if 'const _sync' in s:
    print("JS: 已含 _sync，跳过 ✓")
else:
    anchor = "ci.addEventListener('input',()=>field.classList.toggle('has',!!ci.value));"
    inject = (
        "\n(()=>{if(ci.tagName!=='TEXTAREA')return;"
        "const _sync=()=>{ci.style.height='auto';"
        "ci.style.height=Math.min(Math.max(ci.scrollHeight,22),120)+'px'};"
        "['input','change','paste','focus'].forEach(ev=>ci.addEventListener(ev,()=>setTimeout(_sync,10)));"
        "window.addEventListener('resize',_sync);"
        "setTimeout(_sync,100);_sync()})();"
    )
    s = must_replace(s, anchor, anchor + inject, 'js inject _sync')
    open(p, 'w', encoding='utf-8').write(s)
    print("JS: 注入 _sync ✓")

print("done")
