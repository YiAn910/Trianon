#!/usr/bin/env python3

def must_replace(code, old, new, tag):
    n = code.count(old)
    assert n == 1, f"[{tag}] 锚点命中 {n} 处（应为 1），停止。"
    return code.replace(old, new)

p_css = 'src/rococo_v1.css'
s = open(p_css, encoding='utf-8').read()

# 1. 强制解除外层高度封印
unlock_css = "\n/* === 解除原版高度封印，让 textarea 顺利撑开外框 === */\n.field, .field .ph { height: auto !important; }\n"
if "解除原版高度封印" not in s:
    s += unlock_css
    print("CSS: 已成功注入【解除高度封印】规则 ✓")
else:
    print("CSS: 封印已解除，跳过 ✓")

# 2. 给 textarea 底部留出 44px 的悬浮按钮避让空间
# 精准匹配带 padding-top:2px 的那一段
old_ci_tail = "line-height:1.5;display:block;padding-top:2px}"
new_ci_tail = "line-height:1.5;display:block;padding-top:2px;padding-bottom:44px}"

if "padding-bottom:44px}" not in s:
    s = must_replace(s, old_ci_tail, new_ci_tail, 'rococo_v1.css ci padding-bottom')
    print("CSS: 已成功为 .ci 增加 padding-bottom:44px 避让空间 ✓")
else:
    print("CSS: .ci 已有 padding-bottom:44px，跳过 ✓")

open(p_css, 'w', encoding='utf-8').write(s)
print("=== 完美！脚本执行完毕 ===")
