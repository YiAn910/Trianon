import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 精准切除我上一版添加的“脏初始化代码”
dirty_init = """
      let _needSave = false;
      data.providers.forEach(p => p.models.forEach(m => {
        if (m.isFavorite === undefined) { m.isFavorite = false; _needSave = true; }
      }));
      if (_needSave) saveData(data);"""

if dirty_init in content:
    content = content.replace(dirty_init, "")
    print("🧹 已清理错误的数据初始化代码")
else:
    print("⚠️ 未找到错误的数据初始化代码，可能已经被你手动删了")

# 2. 将所有的 isFavorite 替换回 starred
# 2.1 替换渲染判断
if "if (isActive || m.isFavorite)" in content:
    content = content.replace("if (isActive || m.isFavorite)", "if (isActive || m.starred)")
else:
    print("⚠️ 未找到 (isActive || m.isFavorite)")

# 2.2 替换已收藏判断
if "if (m.isFavorite) {" in content:
    content = content.replace("if (m.isFavorite) {", "if (m.starred) {")
else:
    print("⚠️ 未找到 (m.isFavorite)")

# 2.3 替换点击切换逻辑
if "tm.isFavorite = !tm.isFavorite;" in content:
    content = content.replace("tm.isFavorite = !tm.isFavorite;", "tm.starred = !tm.starred;")
else:
    print("⚠️ 未找到 tm.isFavorite = !tm.isFavorite;")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 数据修复完成，字段已全部统一为 starred！请运行 python build.py")
