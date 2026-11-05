import re

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 用正则精准匹配 const injectRows = () => { ... }; 整个函数
pattern = r"(const injectRows = \(\) => \{[\s\S]*?\n    \};)"

new_block = """const injectRows = () => {
      const mv = document.getElementById('mpMv');
      if (!mv) return;

      // 只清理自己生成的行，不误伤其他元素
      mv.querySelectorAll('.mp-row, .mp-empty-row').forEach(el => el.remove());
      
      const data = getData();
      const active = data.activeModel;
      const header = mv.querySelector('.mp-hd');
      const targetNode = header ? header.nextSibling : mv.firstChild;

      if (!data.providers || data.providers.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'mp-c mp-empty-row tri-preset-row';
        emptyDiv.style.cssText = "color: #7C8DB5; font-size: 13px; padding: 12px 16px; text-align: center;";
        emptyDiv.textContent = "暂无模型，请在“更多模型”中配置";
        mv.insertBefore(emptyDiv, targetNode);
      } else {
        // 提取并排序已收藏的模型
        const starredModels = [];
        (data.providers || []).forEach(p => {
          (p.models || []).forEach(m => {
            if (m && m.starred === true) {
              starredModels.push({ provider: p, model: m });
            }
          });
        });

        starredModels.sort((a, b) => {
          const pNameA = a.provider.name || '';
          const pNameB = b.provider.name || '';
          const mNameA = a.model.name || '';
          const mNameB = b.model.name || '';
          return pNameA.localeCompare(pNameB) || mNameA.localeCompare(mNameB);
        });

        if (starredModels.length === 0) {
          const emptyDiv = document.createElement('div');
          emptyDiv.className = 'mp-c mp-empty-row tri-preset-row';
          emptyDiv.style.cssText = "color: #7C8DB5; font-size: 13px; padding: 12px 16px; text-align: center;";
          emptyDiv.textContent = "暂无收藏的模型，请在“更多模型”中收藏";
          mv.insertBefore(emptyDiv, targetNode);
        } else {
          starredModels.forEach(item => {
            const p = item.provider;
            const m = item.model;
            const row = document.createElement('div');
            row.className = 'mp-c mp-row tri-preset-row';
            row.setAttribute('role', 'menuitemradio');
            const isActive = active && active.providerId === p.id && active.modelId === m.id;
            row.setAttribute('aria-checked', isActive ? 'true' : 'false');
            if (isActive) row.classList.add('on');
            row.style.cursor = 'pointer';

            const b = document.createElement('b');
            b.textContent = m.name;
            row.appendChild(b);

            row.onclick = () => {
              const newData = getData();
              newData.activeModel = { providerId: p.id, modelId: m.id };
              saveData(newData);
              mpop.setAttribute('aria-hidden', 'true');
              mpop.classList.remove('on');
              
              // 安全的兜底写法
              if (typeof renderCatalogueFn === 'function') {
                renderCatalogueFn();
              } else if (typeof window.renderCatalogueFn === 'function') {
                window.renderCatalogueFn();
              }
            };
            mv.insertBefore(row, targetNode);
          });
        }
      }
    };"""

new_content, count = re.subn(pattern, new_block, content)

assert count == 1, f"❌ 正则匹配失败，匹配到了 {count} 处。请确认代码格式！"

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ 正则精准替换成功，兜底逻辑已加入！请运行 python build.py")
