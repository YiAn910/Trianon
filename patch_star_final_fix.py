import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 使用精准切块，直接覆盖整个星星模块（从“收藏星标”到 row.appendChild）
start_marker = "// 2. 收藏星标（带底色圆、白边、质感）"
end_marker = "row.appendChild(actionDiv);"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx) + len(end_marker)

assert start_idx != -1, "❌ 找不到星星注释起点"
assert end_idx != -1, "❌ 找不到 actionDiv 结束点"

new_block = """// 2. 收藏星标（带底色圆、白边、质感）
            if (isActive || m.starred) {
              const starBtn = document.createElement('div');
              starBtn.style.cssText = 'cursor: pointer; display: flex; align-items: center; justify-content: center; width: 32px; height: 32px;';
              
              const starSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
              starSvg.setAttribute('viewBox', '0 0 32 32');
              starSvg.setAttribute('width', '28');
              starSvg.setAttribute('height', '28');
              // 动画过渡时间设为 0.15s，以便和我们后面的 setTimeout 完美契合
              starSvg.style.cssText = 'transition: transform 0.15s ease; transform: scale(1.02) rotate(-10deg); filter: drop-shadow(0px 2px 6px rgba(76, 93, 136, 0.15));';
              
              // 底色浅蓝紫圆
              const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
              bgCircle.setAttribute('cx', '16');
              bgCircle.setAttribute('cy', '16');
              bgCircle.setAttribute('r', '14');
              bgCircle.setAttribute('fill', '#DBE2EF');
              starSvg.appendChild(bgCircle);

              const dStr = 'M16 6 L19.5 13 L27 14 L21.5 19 L23 26.5 L16 22.5 L9 26.5 L10.5 19 L5 14 L12.5 13 Z';
              
              // 外层厚白边
              const starWhite = document.createElementNS('http://www.w3.org/2000/svg', 'path');
              starWhite.setAttribute('d', dStr);
              starWhite.setAttribute('fill', 'none');
              starWhite.setAttribute('stroke', '#FFFFFF');
              starWhite.setAttribute('stroke-width', '3.5');
              starWhite.setAttribute('stroke-linejoin', 'round');
              starSvg.appendChild(starWhite);

              // 内层线条和填充
              const starInner = document.createElementNS('http://www.w3.org/2000/svg', 'path');
              starInner.setAttribute('d', dStr);
              starInner.setAttribute('stroke-width', '1.5');
              starInner.setAttribute('stroke-linejoin', 'round');
              
              if (m.starred) {
                starInner.setAttribute('fill', '#CDD6EB');
                starInner.setAttribute('stroke', '#4C5D88');
              } else {
                starInner.setAttribute('fill', 'transparent');
                starInner.setAttribute('stroke', '#7C8DB5');
              }
              starSvg.appendChild(starInner);
              starBtn.appendChild(starSvg);

              // 点击动画与逻辑
              starBtn.onclick = (e) => {
                e.stopPropagation();
                
                // 1. 播放放大+向左旋转动画
                starSvg.style.transform = 'scale(1.15) rotate(-30deg)';
                
                // 2. 150ms 后动画走完，恢复默认角度
                setTimeout(() => {
                  starSvg.style.transform = 'scale(1.02) rotate(-10deg)';
                }, 150);

                // 3. 更新数据
                const newData = getData();
                const tp = newData.providers.find(x => x.id === p.id);
                if (tp) {
                  const tm = tp.models.find(x => x.id === m.id);
                  if (tm) {
                    tm.starred = !tm.starred;
                    saveData(newData);
                  }
                }
                
                // 4. 等待 250ms（动画播完 + 恢复原位）后再重建列表
                setTimeout(() => {
                  renderCatalogueFn();
                }, 250);
              };
              actionDiv.appendChild(starBtn);
            }
            row.appendChild(actionDiv);"""

content = content[:start_idx] + new_block + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 替换完成，带 strict assert 验证！")
