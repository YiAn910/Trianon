import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 极其安全的单行替换（保留对勾，在前面追加星星）
old_anchor = "row.appendChild(actionDiv);"

new_code = """
            // 收藏星标：仅在选中或已收藏时显示（防止破坏原有布局）
            if (isActive || m.isFavorite) {
              const starBtn = document.createElement('div');
              starBtn.style.cssText = 'cursor: pointer; display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; transition: transform 0.2s;';
              
              const starSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
              starSvg.setAttribute('viewBox', '0 0 24 24');
              starSvg.setAttribute('width', '20');
              starSvg.setAttribute('height', '20');
              
              const starPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
              starPath.setAttribute('d', 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z');
              starPath.setAttribute('stroke-width', '1.5');
              starPath.setAttribute('stroke-linejoin', 'round');
              
              if (m.isFavorite) {
                starPath.setAttribute('fill', '#B48C9C');
                starPath.setAttribute('stroke', '#B48C9C');
                starSvg.style.transform = 'scale(1.1)';
              } else {
                starPath.setAttribute('fill', 'none');
                starPath.setAttribute('stroke', '#9CA8C4');
              }
              
              starSvg.appendChild(starPath);
              starBtn.appendChild(starSvg);
              
              starBtn.onclick = (e) => {
                e.stopPropagation();
                const newData = getData();
                const tp = newData.providers.find(x => x.id === p.id);
                if (tp) {
                  const tm = tp.models.find(x => x.id === m.id);
                  if (tm) {
                    tm.isFavorite = !tm.isFavorite;
                    saveData(newData);
                    renderCatalogueFn();
                  }
                }
              };
              actionDiv.appendChild(starBtn);
            }
            row.appendChild(actionDiv);"""

# 检查锚点是否存在
if old_anchor in content:
    # 注意这里替换的是 row.appendChild(actionDiv); 这 1 行
    content = content.replace(old_anchor, new_code, 1)
    print("✅ 成功注入星星逻辑！")
else:
    print("❌ 找不到锚点 row.appendChild(actionDiv); 请告诉我！")

# 2. 顺手把 isFavorite 初始化补上（加在 data 定义后）
old_getdata = "const data = getData();"
new_getdata = """const data = getData();
      let _needSave = false;
      data.providers.forEach(p => p.models.forEach(m => {
        if (m.isFavorite === undefined) { m.isFavorite = false; _needSave = true; }
      }));
      if (_needSave) saveData(data);"""
      
if old_getdata in content:
    content = content.replace(old_getdata, new_getdata, 1)
    print("✅ 成功补全 isFavorite 字段！")
else:
    print("⚠️ 数据字段可能已存在，跳过。")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("🎉 执行完毕，请运行 python build.py")
