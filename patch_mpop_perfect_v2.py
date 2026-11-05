import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_str = "const injectRows = () => {"
start_idx = content.find(start_str)
assert start_idx != -1, "❌ 找不到 injectRows 函数起点！"

# 【终极定位算法】大括号深度匹配，绝不误删中间的任何代码
brace_start = start_idx + len(start_str) - 1
depth = 1
idx = brace_start + 1

while idx < len(content) and depth > 0:
    if content[idx] == '{':
        depth += 1
    elif content[idx] == '}':
        depth -= 1
    idx += 1

assert depth == 0, "❌ 大括号未闭合，找不到函数终点！"
brace_end = idx

new_block = """const injectRows = () => {
      const mv = document.getElementById('mpMv');
      if (!mv) return;

      // 【修正】只清理自己生成的元素，防误删原版元素
      mv.querySelectorAll('.mp-injected-row').forEach(el => el.remove());
      
      const data = getData();
      const active = data.activeModel;
      
      // 【修正】条件覆盖 targetNode，防打乱正常位置
      const header = mv.querySelector('.mp-hd');
      let targetNode = header ? header.nextElementSibling : mv.firstElementChild;
      
      const allDivs = Array.from(mv.querySelectorAll('div'));
      // 用更精准的查找，只找包含“更多模型”这四个字的叶子节点
      const moreDiv = allDivs.find(el => el.textContent.includes('更多模型') && el.children.length === 0);
      
      if (moreDiv && moreDiv.parentNode) {
        const moreParent = moreDiv.parentNode;
        const tgtOk = targetNode && mv.contains(targetNode);
        // 如果目标节点无效，或者目标节点在“更多模型”之后，才强制覆盖
        const tgtAfterMore = tgtOk && (moreParent.compareDocumentPosition(targetNode) & Node.DOCUMENT_POSITION_FOLLOWING);
        if (!tgtOk || tgtAfterMore) {
          targetNode = moreParent;
        }
      }

      // 【修正】使用 parentNode.insertBefore，完美兼容“更多模型”作为定位点的情况
      const safeInsert = (el) => {
        if (targetNode && mv.contains(targetNode)) {
          targetNode.parentNode.insertBefore(el, targetNode);
        } else {
          mv.appendChild(el);
        }
      };

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
      } else {
        starredModels.sort((a, b) => (a.provider.name || '').localeCompare(b.provider.name || '') || (a.model.name || '').localeCompare(b.model.name || ''));

        starredModels.forEach(item => {
          const p = item.provider;
          const m = item.model;
          
          const row = document.createElement('div');
          // 【修正】绝不覆盖原版 CSS，类名严丝合缝
          row.className = 'mp-c mp-row mp-injected-row tri-preset-row';
          row.setAttribute('role', 'menuitemradio');
          const isActive = active && active.providerId === p.id && active.modelId === m.id;
          
          row.setAttribute('aria-checked', isActive ? 'true' : 'false');
          if (isActive) row.classList.add('on');
          
          const b = document.createElement('b');
          b.textContent = m.name;
          row.appendChild(b);

          row.onclick = () => {
            const newData = getData();
            newData.activeModel = { providerId: p.id, modelId: m.id };
            saveData(newData);
            mpop.setAttribute('aria-hidden', 'true');
            mpop.classList.remove('on');
            
            // 【保留】双兜底
            if (typeof renderCatalogueFn === 'function') {
              renderCatalogueFn();
            } else if (typeof window.renderCatalogueFn === 'function') {
              window.renderCatalogueFn();
            }
          };
          safeInsert(row);
        });
      }
    };"""

content = content[:start_idx] + new_block + content[brace_end:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 完美修复！请运行 node --check src/rococo_v1.js 验证语法")
