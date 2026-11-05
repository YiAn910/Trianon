import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 替换空状态的两个插入
old_empty_insert = "mv.insertBefore(emptyDiv, targetNode);"
new_empty_insert = """if (targetNode && targetNode.parentNode === mv) {
          mv.insertBefore(emptyDiv, targetNode);
        } else {
          mv.appendChild(emptyDiv);
        }"""

count_empty = content.count(old_empty_insert)
assert count_empty == 2, f"❌ 空状态插入锚点异常，匹配到了 {count_empty} 处"
content = content.replace(old_empty_insert, new_empty_insert)

# 2. 替换模型列表的插入
old_row_insert = "mv.insertBefore(row, targetNode);"
new_row_insert = """if (targetNode && targetNode.parentNode === mv) {
            mv.insertBefore(row, targetNode);
          } else {
            mv.appendChild(row);
          }"""

count_row = content.count(old_row_insert)
assert count_row == 1, f"❌ 模型插入锚点异常，匹配到了 {count_row} 处"
content = content.replace(old_row_insert, new_row_insert)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ insertBefore 报错隐患已彻底排除！")
