import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 精准找到设置行状态的代码块
old_code = """          const isActive = active && active.providerId === p.id && active.modelId === m.id;
          row.setAttribute('aria-checked', isActive ? 'true' : 'false');
          if (isActive) row.classList.add('on');
          
          // 恢复 <b> 标签
          const b = document.createElement('b');
          b.textContent = m.name;
          row.appendChild(b);

          // 既然原版没有对勾，我们自己画一个完美蓝色对勾，并让它靠右
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
            checkSvg.style.marginLeft = 'auto'; // 把对勾推到最右边
            row.appendChild(checkSvg);
          }"""

new_code = """          const isActive = active && active.providerId === p.id && active.modelId === m.id;
          row.setAttribute('aria-checked', isActive ? 'true' : 'false');
          
          // 【暴力内联】直接覆盖背景和边框，无视原版任何阻断的 CSS
          if (isActive) {
            row.classList.add('on');
            row.style.setProperty('background-color', '#E8EEF8', 'important');
            row.style.setProperty('border', '1px solid #D0D9E8', 'important');
            row.style.setProperty('border-radius', '6px', 'important');
          } else {
            row.style.setProperty('background-color', '#FFFFFF', 'important');
            row.style.setProperty('border', '1px solid transparent', 'important');
          }
          
          // 恢复 <b> 标签
          const b = document.createElement('b');
          b.textContent = m.name;
          // 确保 b 标签撑开左侧
          b.style.setProperty('flex-grow', '1', 'important');
          b.style.setProperty('text-align', 'left', 'important');
          row.appendChild(b);

          // 手写靠右的蓝色对勾
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
            checkSvg.style.setProperty('margin-left', 'auto', 'important');
            checkSvg.style.setProperty('flex-shrink', '0', 'important');
            row.appendChild(checkSvg);
          }"""

assert old_code in content, "❌ 锚点匹配失败，请确认是否已经跑过 patch_mpop_force_css.py"
content = content.replace(old_code, new_code)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 内联强力样式注入成功！请运行 node --check 并 build")
