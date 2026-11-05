import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_str = "const injectRows = () => {"
end_str = "settingsObserver = new MutationObserver"

start_idx = content.find(start_str)
assert start_idx != -1, "❌ 找不到 injectRows 起点"

end_idx = content.find(end_str, start_idx)
assert end_idx != -1, "❌ 找不到 settingsObserver 终点"
line_start = content.rfind('\n', 0, end_idx) + 1
end_idx = line_start

new_block = """const injectRows = () => {
      const mv = document.getElementById('mpMv');
      if (!mv) return;

      // 1. 清理旧行
      mv.querySelectorAll('.mp-row, .mp-empty-row, .mp-injected-row').forEach(el => el.remove());
      
      const data = getData();
      const active = data.activeModel;
      
      // 2. 寻找“思考”区块或“更多模型”作为锚点
      // 原版的列表其实插在 .mp-hd 后面。我们用 nextElementSibling 跳过换行符
      const header = mv.querySelector('.mp-hd');
      let targetNode = header ? header.nextElementSibling : mv.firstElementChild;
      
      // 兜底：如果目标节点跑到了“更多模型”下面，我们强行把它定位到“更多模型”上面
      // 找包含“更多模型”字样的 div 的父节点
      const allDivs = Array.from(mv.querySelectorAll('div'));
      const moreDiv = allDivs.find(el => el.textContent.includes('更多模型') && el.children.length === 0);
      if (moreDiv && moreDiv.parentNode) {
        targetNode = moreDiv.parentNode;
      }

      // 安全插入函数
      const safeInsert = (el) => {
        if (targetNode && targetNode.parentNode === mv) {
          mv.insertBefore(el, targetNode);
        } else {
          mv.appendChild(el);
        }
      };

      // 3. 提取收藏的数据
      const starredModels = [];
      (data.providers || []).forEach(p => {
        (p.models || []).forEach(m => {
          if (m && m.starred === true) {
            starredModels.push({ provider: p, model: m });
          }
        });
      });

      if (starredModels.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'mp-c mp-empty-row mp-injected-row tri-preset-row';
        emptyDiv.style.cssText = "color: #7C8DB5; font-size: 13px; padding: 12px 16px; text-align: center;";
        emptyDiv.textContent = "暂无收藏的模型，请在“更多模型”中收藏";
        safeInsert(emptyDiv);
        return;
      }

      // 排序
      starredModels.sort((a, b) => (a.provider.name || '').localeCompare(b.provider.name || '') || (a.model.name || '').localeCompare(b.model.name || ''));

      // 4. 渲染列表（完全复刻原版内部结构，防止样式凸出）
      starredModels.forEach(item => {
        const p = item.provider;
        const m = item.model;
        
        const row = document.createElement('div');
        row.className = 'mp-c mp-row mp-injected-row tri-preset-row';
        row.setAttribute('role', 'menuitemradio');
        const isActive = active && active.providerId === p.id && active.modelId === m.id;
        
        // 强制 flex 布局，防止错位
        row.style.cssText = 'display: flex; align-items: center; justify-content: space-between; padding: 10px 16px; cursor: pointer;';
        
        if (isActive) row.classList.add('on');
        
        const b = document.createElement('b');
        b.textContent = m.name;
        row.appendChild(b);

        // 如果选中，补上蓝色的对勾 SVG
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
          checkSvg.style.marginLeft = 'auto';
          row.appendChild(checkSvg);
        }

        row.onclick = () => {
          const newData = getData();
          newData.activeModel = { providerId: p.id, modelId: m.id };
          saveData(newData);
          mpop.setAttribute('aria-hidden', 'true');
          mpop.classList.remove('on');
          
          // 同步刷新全屏页面
          if (typeof renderCatalogueFn === 'function') {
            renderCatalogueFn();
          } else if (typeof window.renderCatalogueFn === 'function') {
            window.renderCatalogueFn();
          }
        };
        safeInsert(row);
      });
    };

    """

content = content[:start_idx] + new_block + content[end_idx:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 完美排版修复完成！请运行 python build.py")
