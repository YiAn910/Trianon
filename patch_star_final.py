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

# 1. 补全 isFavorite 数据初始化
old_getdata = "const data = getData();"
new_getdata = """const data = getData();
      let _needSave = false;
      data.providers.forEach(p => p.models.forEach(m => {
        if (m.isFavorite === undefined) { m.isFavorite = false; _needSave = true; }
      }));
      if (_needSave) saveData(data);"""
if old_getdata in content:
    content = content.replace(old_getdata, new_getdata, 1)
else:
    print("⚠️ 提示: 数据初始化可能已应用过，跳过")

# 2. 注入星星动画 CSS
old_css_anchor = "// ================= UI 接管：全屏页面 (#mdl) ================="
new_css_anchor = """// ================= UI 接管：全屏页面 (#mdl) =================
  if (!document.getElementById('star-anim-style')) {
    const style = document.createElement('style');
    style.id = 'star-anim-style';
    style.textContent = `@keyframes star-pop {
      0% { transform: scale(0.5) rotate(-45deg); opacity: 0; }
      50% { transform: scale(1.3) rotate(15deg); opacity: 1; }
      100% { transform: scale(1) rotate(0); opacity: 1; }
    }`;
    document.head.appendChild(style);
  }
"""
assert old_css_anchor in content, "❌ 锚点2失败：未找到 UI 接管注入点"
content = content.replace(old_css_anchor, new_css_anchor)

# 3. 替换 actionDiv 渲染块
start_marker = "const actionDiv = document.createElement('div');"
end_marker = "row.appendChild(actionDiv);"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx) + len(end_marker)

assert start_idx != -1 and end_idx != -1, "❌ 锚点3失败：未找到 actionDiv 渲染块"

new_block = """const actionDiv = document.createElement('div');
            actionDiv.style.cssText = 'display: flex; align-items: center; margin-left: auto; margin-right: 12px; gap: 16px; height: 32px;';

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

            // 收藏星标（带透明占位和动画）
            const starBtn = document.createElement('div');
            starBtn.style.cssText = 'cursor: pointer; display: flex; align-items: center; justify-content: center; width: 32px; height: 32px;';
            
            const starSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            starSvg.setAttribute('viewBox', '0 0 24 24');
            starSvg.setAttribute('width', '22');
            starSvg.setAttribute('height', '22');
            starSvg.style.cssText = 'transition: opacity 0.2s;';
            const starPath = "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z";

            if (m.isFavorite) {
              // 已收藏：实心星 + 弹跳动画
              starSvg.style.opacity = '1';
              starSvg.innerHTML = `<path d="${starPath}" fill="#B48C9C" stroke="#B48C9C" stroke-width="1.5" stroke-linejoin="round"></path>`;
              starSvg.style.animation = 'star-pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards';
            } else if (isActive) {
              // 选中未收藏：空心星
              starSvg.style.opacity = '0.5';
              starSvg.innerHTML = `<path d="${starPath}" fill="none" stroke="#2E3B68" stroke-width="1.5" stroke-linejoin="round"></path>`;
            } else {
              // 未选中未收藏：透明占位
              starSvg.style.opacity = '0'; 
              starSvg.innerHTML = `<path d="${starPath}" fill="none" stroke="#2E3B68" stroke-width="1.5" stroke-linejoin="round"></path>`;
            }
            
            // 悬浮交互（电脑端）
            starBtn.onmouseenter = () => { if (!m.isFavorite && !isActive) starSvg.style.opacity = '0.2'; };
            starBtn.onmouseleave = () => { if (!m.isFavorite && !isActive) starSvg.style.opacity = '0'; };
            starBtn.appendChild(starSvg);

            // 点击星星：阻断冒泡并切换状态
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
