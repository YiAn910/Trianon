import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 将清理范围扩大：不仅清理自己注入的，也要清理原版的演示数据（.mp-row 和 .tri-preset-row）
old_clean = "mv.querySelectorAll('.mp-injected-row').forEach(el => el.remove());"
new_clean = "mv.querySelectorAll('.mp-row, .tri-preset-row, .mp-injected-row').forEach(el => el.remove());"

count = content.count(old_clean)
assert count == 1, f"❌ 锚点匹配异常，找到 {count} 处清理逻辑"

content = content.replace(old_clean, new_clean)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 原版 Demo 数据已被清理，现在只显示你的收藏！请运行 python build.py")
