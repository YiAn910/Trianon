import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 用切片方式，精准替换整个 actionDiv 块以及下方的 row.onclick（确保关闭逻辑生效）
start_marker = "const actionDiv = document.createElement('div');"
end_marker = "mdList.appendChild(row);"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx) + len(end_marker)

assert start_idx != -1, "❌ 找不到 actionDiv 起点"
assert end_idx != -1, "❌ 找不到 mdList.appendChild(row); 终点"

new_block = """const actionDiv = document.createElement('div');
            actionDiv.style.cssText = 'display: flex; align-items: center; margin-left: auto; margin-right: 12px; gap: 16px;';

            // 1. 蓝色对勾
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

            // 2. 收藏星标
            if (isActive || m.starred) {
              const starBtn = document.createElement('div');
              starBtn.style.cssText = 'cursor: pointer; display: flex; align-items: center; justify-content: center; width: 32px; height: 32px;';
              
              const starSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
              starSvg.setAttribute('viewBox', '0 0 32 32');
              starSvg.setAttribute('width', '32');
              starSvg.setAttribute('height', '32');
              // 动画时间 0.2s
              starSvg.style.cssText = 'transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); transform: scale(1) rotate(0deg); filter: drop-shadow(0px 3px 8px rgba(76, 93, 136, 0.3));';
              
              // 渐变定义
              const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
              const grad = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
              grad.setAttribute('id', 'starGrad');
              grad.setAttribute('x1', '0%'); grad.setAttribute('y1', '0%');
              grad.setAttribute('x2', '100%'); grad.setAttribute('y2', '100%');
              const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
              stop1.setAttribute('offset', '0%'); stop1.setAttribute('stop-color', '#F3F6FC');
              const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
              stop2.setAttribute('offset', '100%'); stop2.setAttribute('stop-color', '#B8C5E0');
              grad.appendChild(stop1); grad.appendChild(stop2);
              defs.appendChild(grad);
              starSvg.appendChild(defs);

              // 严丝合缝的正五角星路径
              const dStr = 'M16 4 L19.2 11.6 L27.4 12.3 L21.2 17.7 L23 25.7 L16 21.5 L9 25.7 L10.8 17.7 L4.6 12.3 L12.8 11.6 Z';
              
              // 外层加粗白边
              const starWhite = document.createElementNS('http://www.w3.org/2000/svg', 'path');
              starWhite.setAttribute('d', dStr);
              starWhite.setAttribute('fill', 'none');
              starWhite.setAttribute('stroke', '#FFFFFF');
              starWhite.setAttribute('stroke-width', '4.5');
              starWhite.setAttribute('stroke-linejoin', 'round');
              starSvg.appendChild(starWhite);

              // 内层填充与描边
              const starInner = document.createElementNS('http://www.w3.org/2000/svg', 'path');
              starInner.setAttribute('d', dStr);
              starInner.setAttribute('stroke-width', '1.5');
              starInner.setAttribute('stroke-linejoin', 'round');
              
              if (m.starred) {
                starInner.setAttribute('fill', 'url(#starGrad)');
                starInner.setAttribute('stroke', '#6F82AC');
              } else {
                starInner.setAttribute('fill', 'transparent');
                starInner.setAttribute('stroke', '#9CA8C4');
              }
              starSvg.appendChild(starInner);

              // 白色斜杠高光
              if (m.starred) {
                const slash = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                slash.setAttribute('d', 'M13 10 L17 10'); // 一条短短的白杠
                slash.setAttribute('stroke', '#FFFFFF');
                slash.setAttribute('stroke-width', '2');
                slash.setAttribute('stroke-linecap', 'round');
                starSvg.appendChild(slash);
              }

              starBtn.appendChild(starSvg);

              // 收藏点击逻辑
              starBtn.onclick = (e) => {
                e.stopPropagation(); // 阻断冒泡，不触发选中
                starSvg.style.transform = 'scale(1.1) rotate(15deg)'; // 快速弹一下
                setTimeout(() => {
                  starSvg.style.transform = 'scale(1) rotate(0deg)';
                }, 150);

                const newData = getData();
                const tp = newData.providers.find(x => x.id === p.id);
                if (tp) {
                  const tm = tp.models.find(x => x.id === m.id);
                  if (tm) {
                    tm.starred = !tm.starred;
                    saveData(newData);
                    setTimeout(() => { renderCatalogueFn(); }, 150);
                  }
                }
              };
              actionDiv.appendChild(starBtn);
            }
            row.appendChild(actionDiv);

            // 选中模型点击事件
            row.onclick = () => {
              const newData = getData();
              newData.activeModel = { providerId: p.id, modelId: m.id };
              saveData(newData);
              
              // 关闭全屏模型界面
              const mdl = document.getElementById('mdl');
              if (mdl) mdl.setAttribute('aria-hidden', 'true');
              
              // 强制关闭弹窗并清除状态
              const mpop = document.getElementById('mpop');
              if (mpop) {
                mpop.setAttribute('aria-hidden', 'true');
                mpop.classList.remove('on');
              }
              
              renderCatalogueFn();
            };
            mdList.appendChild(row);"""

content = content[:start_idx] + new_block + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 脚本执行成功！完美几何星、阴影、高光、渐变、点击关闭 已全部注入！")
