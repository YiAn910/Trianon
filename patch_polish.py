#!/usr/bin/env python3

def must_replace(code, old, new, tag):
    n = code.count(old)
    assert n == 1, f"[{tag}] 锚点命中 {n} 处（应为 1），停止。"
    return code.replace(old, new)

p_css = 'src/rococo_v1.css'
s = open(p_css, encoding='utf-8').read()

# 1. 移除 .ph 上的冗余 min-height:30px
old_ph = ".field .ph{position:relative;cursor:text;padding:4px 0}"
new_ph = ".field .ph{position:relative;cursor:text;padding:4px 0}"
# 兼容之前可能留下的带 min-height 的版本
if s.count(".field .ph{position:relative;cursor:text;min-height:30px;padding:4px 0}") == 1:
    s = s.replace(".field .ph{position:relative;cursor:text;min-height:30px;padding:4px 0}", new_ph)
    print("CSS: 移除 .ph 上的冗余 min-height:30px ✓")
elif s.count(".field .ph{position:relative;cursor:text;min-height:30px}") == 1:
    s = s.replace(".field .ph{position:relative;cursor:text;min-height:30px}", new_ph)
    print("CSS: 移除 .ph 上的冗余 min-height:30px ✓")
else:
    # 如果当前已经是无 min-height 的纯净版，再检查一下是否包含 padding:4px 0
    if new_ph not in s:
        print("警告: 未识别到 .ph 的当前形态，请确认是否影响")
    else:
        print("CSS: .ph 已无冗余 min-height ✓")

# 2. 给 .ph-txt 补齐 line-height 和 font-size
# 兼容 top:4px 和 top:2px 两种情况（因为历史版本可能改过）
target_top4 = ".field .ph-txt{position:absolute;left:0;top:4px;pointer-events:none;transition:opacity .2s}"
target_top2 = ".field .ph-txt{position:absolute;left:0;top:2px;pointer-events:none;transition:opacity .2s}"
target_top6 = ".field .ph-txt{position:absolute;left:0;top:6px;pointer-events:none;transition:opacity .2s}"

added_line = ";font-size:14.5px;line-height:1.5}"

if target_top4 in s:
    s = s.replace(target_top4, target_top4.replace("}", added_line))
    print("CSS: 为 .ph-txt 补齐 line-height (top:4px) ✓")
elif target_top2 in s:
    s = s.replace(target_top2, target_top2.replace("}", added_line))
    print("CSS: 为 .ph-txt 补齐 line-height (top:2px) ✓")
elif target_top6 in s:
    s = s.replace(target_top6, target_top6.replace("}", added_line))
    print("CSS: 为 .ph-txt 补齐 line-height (top:6px) ✓")
else:
    print("警告: 未找到精确的 .ph-txt 锚点，请检查是否已有 line-height 或格式差异")

open(p_css, 'w', encoding='utf-8').write(s)
print("=== 视觉微调完成 ===")
