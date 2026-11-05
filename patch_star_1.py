import os
import shutil

file_path = 'src/rococo_v1.js'
backup_path = 'src/rococo_v1.js.bak'

if not os.path.exists(backup_path):
    shutil.copy(file_path, backup_path)
    print("✅ 已备份原文件至", backup_path)
else:
    print("✅ 备份文件已存在，跳过备份。")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 数据初始化（给没有 isFavorite 的模型补上 false）
old_getdata = "const data = getData();"
new_getdata = """const data = getData();
      let _needSave = false;
      data.providers.forEach(p => p.models.forEach(m => {
        if (m.isFavorite === undefined) { m.isFavorite = false; _needSave = true; }
      }));
      if (_needSave) saveData(data);"""

assert old_getdata in content, "❌ 锚点1失败：未找到 const data = getData();"
content = content.replace(old_getdata, new_getdata)

# 2. actionDiv 替换（使用精准定位，避免缩进干扰）
start_marker = "const actionDiv = document.createElement('div');"
end_marker = "row.appendChild(actionDiv);"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx) + len(end_marker)

assert start_idx != -1 and end_idx != -1, "❌ 锚点2失败：未找到 actionDiv 渲染块"

new_block = """const actionDiv = document.createElement('div');
            actionDiv.style.cssText = 'display: flex; align-items: center; margin-left: auto; margin-right: 12px; gap: 12px;';

            if (isActive) {
              const checkSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
              checkSvg.setAttribute('width', '20');
              checkSvg.setAttribute('height', '20');
              checkSvg.setAttribute('viewBox', '0 0 24 24');
              checkSvg.setAttribute('fill', 'none');
              checkSvg.setAttribute('stroke', '#2E3B68');
              checkSvg.setAttribute('stroke-width', '2.5');
              checkSvg.setAttribute('stroke-linecap', 'round');
              checkSvg.setAttribute('stroke-linejoin', 'round');
              checkSvg.innerHTML = '<polyline points="20 6 9 17 4 12"></polyline>';
              actionDiv.appendChild(checkSvg);
            }

            // 收藏星标
            const starBtn = document.createElement('div');
            starBtn.style.cssText = 'cursor: pointer; display: flex; align-items: center; justify-content: center; width: 28px; height: 28px; transition: transform 0.2s;';
            starBtn.onmouseover = () => starBtn.style.transform = 'scale(1.15)';
            starBtn.onmouseout = () => starBtn.style.transform = 'scale(1)';
            
            const starSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            starSvg.setAttribute('viewBox', '-24 -24 48 48');
            starSvg.setAttribute('width', '24');
            starSvg.setAttribute('height', '24');
            starSvg.style.cssText = 'transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);';
            
            if (m.isFavorite) {
              starSvg.style.transform = 'rotate(90deg) scale(1.1)';
              starSvg.innerHTML = `<path class="ray" d="M-22 0 H22 M0 -22 V22" stroke="#B48C9C" stroke-width="1" fill="none" opacity="0.4"></path>
                <path class="pt" d="M0 -12 C1.92 -1.92 1.92 1.92 12 0 C1.92 1.92 1.92 1.92 0 12 C-1.92 1.92 -1.92 1.92 -12 0 C-1.92 -1.92 -1.92 -1.92 0 -12Z" fill="#D19C97" stroke="#D19C97" stroke-width="1.5"></path>`;
            } else {
              starSvg.style.opacity = '0.3';
              starSvg.innerHTML = `<path class="ray" d="M-22 0 H22 M0 -22 V22" stroke="#9CA8C4" stroke-width="1" fill="none"></path>
                <path class="pt" d="M0 -12 C1.92 -1.92 1.92 1.92 12 0 C1.92 1.92 1.92 1.92 0 12 C-1.92 1.92 -1.92 1.92 -12 0 C-1.92 -1.92 -1.92 -1.92 0 -12Z" fill="none" stroke="#9CA8C4" stroke-width="1.5"></path>`;
            }
            starBtn.appendChild(starSvg);

            // 点击星星：切换收藏状态并阻断冒泡
            starBtn.onclick = (e) => {
              e.stopPropagation();
              const newData = getData();
              const targetProvider = newData.providers.find(x => x.id === p.id);
              if (targetProvider) {
                const targetModel = targetProvider.models.find(x => x.id === m.id);
                if (targetModel) {
                  targetModel.isFavorite = !targetModel.isFavorite;
                  saveData(newData);
                  renderCatalogueFn();
                }
              }
            };
            actionDiv.appendChild(starBtn);
            row.appendChild(actionDiv);"""

content = content[:start_idx] + new_block + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 替换成功！请运行 python build.py 重新构建。")
