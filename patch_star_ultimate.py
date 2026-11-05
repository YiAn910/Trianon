import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 定位 actionDiv 的起始和结束，进行整块安全替换
start_marker = "const actionDiv = document.createElement('div');"
end_marker = "row.appendChild(actionDiv);"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx) + len(end_marker)

assert start_idx != -1 and end_idx != -1, "❌ 锚点失败：未找到 actionDiv 渲染块"

new_block = """const actionDiv = document.createElement('div');
            actionDiv.style.cssText = 'display: flex; align-items: center; margin-left: auto; margin-right: 12px; gap: 16px;';

            // 1. 找回蓝色的选中对勾
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

            // 2. 收藏星标（带底色圆、白边、质感）
            if (isActive || m.isFavorite) {
              const starBtn = document.createElement('div');
              starBtn.style.cssText = 'cursor: pointer; display: flex; align-items: center; justify-content: center; width: 32px; height: 32px;';
              
              const starSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
              starSvg.setAttribute('viewBox', '0 0 32 32');
              starSvg.setAttribute('width', '28');
              starSvg.setAttribute('height', '28');
              // 初始状态，准备用来做动画
              starSvg.style.cssText = 'transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); transform: scale(1) rotate(0deg);';
              
              // 底色浅蓝紫圆
              const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
              bgCircle.setAttribute('cx', '16');
              bgCircle.setAttribute('cy', '16');
              bgCircle.setAttribute('r', '14');
              bgCircle.setAttribute('fill', '#F3F5FA'); // 图上的淡色底
              starSvg.appendChild(bgCircle);

              // 五角星路径 (中心点在 16,16)
              const dStr = 'M16 6 L19.5 13 L27 14 L21.5 19 L23 26.5 L16 22.5 L9 26.5 L10.5 19 L5 14 L12.5 13 Z';
              
              // 外层厚白边（模拟珐琅质感）
              const starWhite = document.createElementNS('http://www.w3.org/2000/svg', 'path');
              starWhite.setAttribute('d', dStr);
              starWhite.setAttribute('fill', 'none');
              starWhite.setAttribute('stroke', '#FFFFFF');
              starWhite.setAttribute('stroke-width', '4');
              starWhite.setAttribute('stroke-linejoin', 'round');
              starSvg.appendChild(starWhite);

              // 内层线条和填充
              const starInner = document.createElementNS('http://www.w3.org/2000/svg', 'path');
              starInner.setAttribute('d', dStr);
              starInner.setAttribute('stroke-width', '1.5');
              starInner.setAttribute('stroke-linejoin', 'round');
              
              if (m.isFavorite) {
                // 已收藏：淡紫蓝填充 + 深蓝灰描边
                starInner.setAttribute('fill', '#CDD6EB');
                starInner.setAttribute('stroke', '#4C5D88');
                starSvg.style.transform = 'scale(1.05) rotate(10deg)'; // 略微倾斜
              } else {
                // 未选中未收藏：透明填充 + 灰蓝描边
                starInner.setAttribute('fill', 'transparent');
                starInner.setAttribute('stroke', '#7C8DB5');
              }
              starSvg.appendChild(starInner);
              starBtn.appendChild(starSvg);

              // 点击动画与逻辑
              starBtn.onclick = (e) => {
                e.stopPropagation(); // 阻断选中，保证选中的弹窗不关
                
                // 播放你说的：放大 + 旋转
                starSvg.style.transform = 'scale(1.3) rotate(30deg)';
                setTimeout(() => {
                  starSvg.style.transform = 'scale(1) rotate(0deg)';
                }, 150);

                const newData = getData();
                const tp = newData.providers.find(x => x.id === p.id);
                if (tp) {
                  const tm = tp.models.find(x => x.id === m.id);
                  if (tm) {
                    tm.isFavorite = !tm.isFavorite;
                    saveData(newData);
                    // 延迟一点刷新页面，让旋转动画播完
                    setTimeout(() => renderCatalogueFn(), 200);
                  }
                }
              };
              actionDiv.appendChild(starBtn);
            }
            row.appendChild(actionDiv);"""

content = content[:start_idx] + new_block + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 对勾已找回，高颜值星星已上线！请运行 python build.py")
