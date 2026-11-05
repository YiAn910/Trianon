import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 我们精确查找上一版注入的回调代码
old_callback = """            // 同作用域直接调用，兜底防错
            if (typeof renderCatalogueFn === 'function') {
              renderCatalogueFn();
            }"""

new_callback = """            // 同作用域直接调用，并且加上 window 兜底
            if (typeof renderCatalogueFn === 'function') {
              renderCatalogueFn();
            } else if (typeof window.renderCatalogueFn === 'function') {
              window.renderCatalogueFn();
            }"""

# 严格检查匹配次数，确保只替换一次
count = content.count(old_callback)
assert count == 1, f"❌ 锚点匹配异常，匹配到了 {count} 处。可能原代码没跑过上一版，或者有重复。"

content = content.replace(old_callback, new_callback)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 双兜底逻辑已完美加回！")
print("👉 请先运行 node --check src/rococo_v1.js 确认语法无误，再运行 python build.py")
