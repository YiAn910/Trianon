#!/usr/bin/env python3

p_css = 'src/rococo_v1.css'
s = open(p_css, encoding='utf-8').read()

# 要追加的补丁规则（使用 !important 确保最高优先级生效）
patch_css = """
/* === 终极修复：解除高度封印 + 底部避让空间 === */
.field, .field .ph { height: auto !important; }
.field .ph .ci { padding-bottom: 44px !important; }
"""

if "终极修复：解除高度封印" not in s:
    s += "\n" + patch_css
    open(p_css, 'w', encoding='utf-8').write(s)
    print("CSS: 已成功注入【终极修复】补丁 ✓")
else:
    print("CSS: 补丁已存在，跳过 ✓")

print("=== 执行完毕，请重新构建 ===")
