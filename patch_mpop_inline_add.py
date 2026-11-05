import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 插入高亮底色和边框
anchor1 = "if (isActive) row.classList.add('on');"
inject1 = """if (isActive) row.classList.add('on');
          if (isActive) {
            row.style.setProperty('background-color', '#E8EEF8', 'important');
            row.style.setProperty('border', '1px solid #D0D9E8', 'important');
            row.style.setProperty('border-radius', '6px', 'important');
          } else {
            row.style.setProperty('background-color', '#FFFFFF', 'important');
            row.style.setProperty('border', '1px solid transparent', 'important');
          }"""
assert anchor1 in content, "❌ 找不到 isActive 锚点"
content = content.replace(anchor1, inject1)

# 2. 确保文字撑开左侧
anchor2 = "row.appendChild(b);"
inject2 = """b.style.setProperty('flex-grow', '1', 'important');
          b.style.setProperty('text-align', 'left', 'important');
          row.appendChild(b);"""
assert anchor2 in content, "❌ 找不到 appendChild(b) 锚点"
content = content.replace(anchor2, inject2)

# 3. 确保对勾靠右且不被压缩
anchor3 = "checkSvg.style.marginLeft = 'auto';"
inject3 = """checkSvg.style.setProperty('margin-left', 'auto', 'important');
            checkSvg.style.setProperty('flex-shrink', '0', 'important');"""
assert anchor3 in content, "❌ 找不到 marginLeft 锚点"
content = content.replace(anchor3, inject3)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 暴力内联样式追加成功！")
