import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_str = "const injectRows = () => {"
start_idx = content.find(start_str)

assert start_idx != -1, "❌ 找不到 injectRows 函数起点！"

# 【终极定位算法】计算大括号深度，精准寻找函数结束的 }
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
brace_end = idx # 指向结束大括号 } 的下一个字符

# 替换原函数
new_block = """const injectRows = () => {
      const mv = document.getElementById('mpMv');
      if (!mv) return;

      // 【专属类名】只清理我们注入的行
      mv.querySelectorAll('.mp-injected-row').forEach(el => el.remove());
      
      const data = getData();
      const active = data.activeModel;
      const header = mv.querySelector('.mp-hd');
      const targetNode = header ? header.nextSibling : mv.firstChild;

      // 提取所有已收藏的模型
      const starredModels = [];
      (data.providers || []).forEach(p => {
        (p.models || []).forEach(m => {
          if (m && m.starred === true) {
            starredModels.push({ provider: p, model: m });
          }
        });
      });

      // 排序逻辑
      starredModels.sort((a, b) => {
        const pNameA = a.provider.name || '';
        const pNameB = b.provider.name || '';
        const mNameA = a.model.name || '';
        const mNameB = b.model.name || '';
        return pNameA.localeCompare(pNameB) || mNameA.localeCompare(mNameB);
      });

      if (!data.providers || data.providers.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'mp-c mp-empty-row mp-injected-row tri-preset-row';
        emptyDiv.style.cssText = "color: #7C8DB5; font-size: 13px; padding: 12px 16px; text-align: center;";
        emptyDiv.textContent = "暂无模型，请在“更多模型”中配置";
        mv.insertBefore(emptyDiv, targetNode);
      } else if (starredModels.length === 0) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'mp-c mp-empty-row mp-injected-row tri-preset-row';
        emptyDiv.style.cssText = "color: #7C8DB5; font-size: 13px; padding: 12px 16px; text-align: center;";
        emptyDiv.textContent = "暂无收藏的模型，请在“更多模型”中收藏";
        mv.insertBefore(emptyDiv, targetNode);
      } else {
        starredModels.forEach(item => {
          const p = item.provider;
          const m = item.model;
          
          const row = document.createElement('div');
          // 保留原版样式类，加上我们的专属标记类
          row.className = 'mp-c mp-row mp-injected-row tri-preset-row';
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
            
            // 同作用域直接调用，兜底防错
            if (typeof renderCatalogueFn === 'function') {
              renderCatalogueFn();
            }
          };
          mv.insertBefore(row, targetNode);
        });
      }
    }"""

content = content[:start_idx] + new_block + content[brace_end:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 括号深度匹配完成，专属类名已注入！请运行 python build.py")
