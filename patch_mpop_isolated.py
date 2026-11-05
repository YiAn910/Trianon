import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_str = "const injectRows = () => {"
start_idx = content.find(start_str)
assert start_idx != -1, "❌ 找不到 injectRows 函数起点！"
assert content.find(start_str, start_idx + 1) == -1, "❌ 发现多个 injectRows 定义！"

# 精准大括号定位
brace_start = start_idx + len(start_str) - 1
depth = 1
idx = brace_start + 1
n = len(content)
in_single = False; in_double = False; in_template = False; in_comment_line = False; in_comment_block = False

while idx < n and depth > 0:
    c = content[idx]
    nxt = content[idx+1] if idx+1 < n else ''
    if in_comment_line:
        if c == '\n': in_comment_line = False
    elif in_comment_block:
        if c == '*' and nxt == '/': in_comment_block = False; idx += 1
    elif in_single:
        if c == '\\': idx += 1
        elif c == "'": in_single = False
    elif in_double:
        if c == '\\': idx += 1
        elif c == '"': in_double = False
    elif in_template:
        if c == '\\': idx += 1
        elif c == '`': in_template = False
    else:
        if c == '/' and nxt == '/': in_comment_line = True; idx += 1
        elif c == '/' and nxt == '*': in_comment_block = True; idx += 1
        elif c == "'": in_single = True
        elif c == '"': in_double = True
        elif c == '`': in_template = True
        elif c == '{': depth += 1
        elif c == '}': depth -= 1
    idx += 1

assert depth == 0, "❌ 大括号未闭合，找不到函数终点！"

brace_end = idx
while brace_end < n and content[brace_end] in ' \t':
    brace_end += 1
if brace_end < n and content[brace_end] == ';':
    brace_end += 1
if brace_end < n and content[brace_end] == '\r':
    brace_end += 1
if brace_end < n and content[brace_end] == '\n':
    brace_end += 1

new_block = """const injectRows = () => {
      const mv = document.getElementById('mpMv');
      if (!mv) return;

      // 【彻底隔离】清理原版假数据，以及我们自己生成的数据（用专属类名 tri-custom-row）
      mv.querySelectorAll('.mp-row, .tri-custom-row, .mp-empty-row').forEach(el => el.remove());
      
      const data = getData();
      const active = data.activeModel;
      
      const header = mv.querySelector('.mp-hd');
      let targetNode = header ? header.nextElementSibling : mv.firstElementChild;
      
      const allDivs = Array.from(mv.querySelectorAll('div'));
      const moreDiv = allDivs.find(el => el.textContent.includes('更多模型') && el.children.length === 0);
      
      if (moreDiv && moreDiv.parentNode && moreDiv.parentNode !== mv) {
        const moreParent = moreDiv.parentNode;
        const tgtOk = targetNode && mv.contains(targetNode) && targetNode !== mv;
        const tgtAfterMore = tgtOk && (moreParent.compareDocumentPosition(targetNode) & Node.DOCUMENT_POSITION_FOLLOWING);
        if (!tgtOk || tgtAfterMore) {
          targetNode = moreParent;
        }
      }

      const safeInsert = (el) => {
        if (targetNode && targetNode !== mv && mv.contains(targetNode)) {
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
        emptyDiv.className = 'tri-custom-row mp-empty-row';
        emptyDiv.style.cssText = "color: #7C8DB5; font-size: 13px; padding: 16px; text-align: center; width: 100%; box-sizing: border-box;";
        emptyDiv.textContent = (!data.providers || data.providers.length === 0) 
            ? "暂无模型，请在「更多模型」中配置" 
            : "暂无收藏的模型，请在「更多模型」中收藏";
        safeInsert(emptyDiv);
      } else {
        starredModels.sort((a, b) => (a.provider.name || '').localeCompare(b.provider.name || '') || (a.model.name || '').localeCompare(b.model.name || ''));

        starredModels.forEach(item => {
          const p = item.provider;
          const m = item.model;
          
          const row = document.createElement('div');
          // 不起原版类名，彻底避开原版死板 CSS 的干扰
          row.className = 'tri-custom-row';
          row.setAttribute('data-m', m.name);
          
          // 用内联样式手绘完美 UI
          let baseCss = 'display: flex; align-items: center; justify-content: space-between; padding: 10px 16px; margin: 0 16px 6px 16px; border-radius: 6px; cursor: pointer; box-sizing: border-box; transition: background 0.2s;';
          
          const isActive = active && active.providerId === p.id && active.modelId === m.id;
          if (isActive) {
            baseCss += ' background-color: #E8EEF8; border: 1px solid #D0D9E8;';
          } else {
            baseCss += ' background-color: #FFFFFF; border: 1px solid #EAEAEA;';
          }
          row.style.cssText = baseCss;
          
          // 字体标签
          const textSpan = document.createElement('span');
          textSpan.textContent = m.name;
          textSpan.style.cssText = 'color: #2E3B68; font-size: 14px; font-weight: 500;';
          row.appendChild(textSpan);

          // 选中时的蓝色对勾
          if (isActive) {
            const checkSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            checkSvg.setAttribute('width', '18');
            checkSvg.setAttribute('height', '18');
            checkSvg.setAttribute('viewBox', '0 0 24 24');
            checkSvg.setAttribute('fill', 'none');
            checkSvg.setAttribute('stroke', '#2E3B68');
            checkSvg.setAttribute('stroke-width', '2.5');
            checkSvg.setAttribute('stroke-linecap', 'round');
            checkSvg.setAttribute('stroke-linejoin', 'round');
            checkSvg.innerHTML = '<polyline points="20 6 9 17 4 12"></polyline>';
            row.appendChild(checkSvg);
          }

          // 悬浮交互
          row.onmouseenter = () => { if (!isActive) row.style.backgroundColor = '#F8FAFC'; };
          row.onmouseleave = () => { if (!isActive) row.style.backgroundColor = '#FFFFFF'; };

          row.onclick = () => {
            const newData = getData();
            newData.activeModel = { providerId: p.id, modelId: m.id };
            saveData(newData);
            
            if (mpop) {
              mpop.setAttribute('aria-hidden', 'true');
              mpop.classList.remove('on');
            }
            
            if (typeof renderCatalogueFn === 'function') {
              renderCatalogueFn();
            } else if (typeof window.renderCatalogueFn === 'function') {
              window.renderCatalogueFn();
            }
          };
          safeInsert(row);
        });
      }
    };
"""

content = content[:start_idx] + new_block + content[brace_end:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 彻底隔离原版 CSS 版注入成功！请运行 node --check 并 build")
