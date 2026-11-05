import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修复 ID 唯一性：加入 encodeURIComponent 动态生成
old_grad = "grad.setAttribute('id', 'starGrad');"
new_grad = "const safeId = 'starGrad-' + encodeURIComponent(p.id) + '-' + encodeURIComponent(m.id);\n              grad.setAttribute('id', safeId);"
assert old_grad in content, "❌ 锚点失败：找不到 grad.setAttribute"
content = content.replace(old_grad, new_grad)

old_fill = "starInner.setAttribute('fill', 'url(#starGrad)');"
new_fill = "starInner.setAttribute('fill', 'url(#' + safeId + ')');"
assert old_fill in content, "❌ 锚点失败：找不到 starInner 的 fill"
content = content.replace(old_fill, new_fill)

# 2. 修复动画时序：transition 缩减为 0.15s，重建延后至 200ms
old_css = "transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); transform: scale(1) rotate(0deg); filter: drop-shadow(0px 3px 8px rgba(76, 93, 136, 0.3));"
new_css = "transition: transform 0.15s cubic-bezier(0.175, 0.885, 0.32, 1.275); transform: scale(1) rotate(0deg); filter: drop-shadow(0px 3px 8px rgba(76, 93, 136, 0.3));"
assert old_css in content, "❌ 锚点失败：找不到 CSS transition"
content = content.replace(old_css, new_css)

# 3. 加上 null 检查，且延迟改为 200ms
old_timeout = "setTimeout(() => { renderCatalogueFn(); }, 150);"
new_timeout = "setTimeout(() => { if (typeof renderCatalogueFn === 'function') renderCatalogueFn(); }, 200);"
assert old_timeout in content, "❌ 锚点失败：找不到星星点击的 setTimeout"
content = content.replace(old_timeout, new_timeout)

# 4. 顺便把 row.onclick 里面的 renderCatalogueFn 也加上 null 检查
old_onclick = "renderCatalogueFn();\n            };\n            mdList.appendChild(row);"
new_onclick = "if (typeof renderCatalogueFn === 'function') renderCatalogueFn();\n            };\n            mdList.appendChild(row);"
assert old_onclick in content, "❌ 锚点失败：找不到 row.onclick 里的 renderCatalogueFn"
content = content.replace(old_onclick, new_onclick)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 架构级修复完成！请运行 python build.py")
