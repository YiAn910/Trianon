#!/usr/bin/env python3

p_css = 'src/rococo_v1.css'
s = open(p_css, encoding='utf-8').read()

# 1. 把 .ph 的 min-height:30px 加回来作为兜底
old_ph = ".field .ph{position:relative;cursor:text;padding:4px 0}"
new_ph = ".field .ph{position:relative;cursor:text;min-height:30px;padding:4px 0}"

if old_ph in s:
    s = s.replace(old_ph, new_ph)
    print("CSS: 恢复 .ph 的 min-height:30px 兜底 ✓")
elif new_ph in s:
    print("CSS: .ph 已有 min-height:30px，跳过 ✓")
else:
    print("⚠️ 警告: 未识别到 .ph 的形态，请手动检查第 9 行")

# 2. 强制统一子元素 em 和 .pht 的行高/字号（防覆盖）
old_txt = ".field .ph-txt{position:absolute;left:0;top:2px;pointer-events:none;transition:opacity .2s;font-size:14.5px;line-height:1.5}"
# 如果当前是 top:4px，也兼容一下
old_txt4 = ".field .ph-txt{position:absolute;left:0;top:4px;pointer-events:none;transition:opacity .2s;font-size:14.5px;line-height:1.5}"

if "font-size:14.5px;line-height:1.5}" in s and ".field .ph-txt" in s:
    print("CSS: .ph-txt 已含 line-height ✓")
else:
    # 兜底，如果上面的匹配失败，暴力给 .ph-txt 加
    if old_txt in s:
        s = s.replace(old_txt, old_txt + "\n.field .ph-txt em,.field .ph-txt .pht{font-size:inherit;line-height:inherit;}")
        print("CSS: 补齐 .ph-txt 子元素继承 ✓")
    elif old_txt4 in s:
        s = s.replace(old_txt4, old_txt4 + "\n.field .ph-txt em,.field .ph-txt .pht{font-size:inherit;line-height:inherit;}")
        print("CSS: 补齐 .ph-txt 子元素继承 ✓")

open(p_css, 'w', encoding='utf-8').write(s)
print("=== 兜底与清理完成 ===")
