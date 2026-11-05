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

      // 【最高权重样式注入】防原版 CSS 覆盖
      if (!document.getElementById('mp-inject-style')) {
        const style = document.createElement('style');
        style.id = 'mp-inject-style';
        style.textContent = `
          #mpMv .mp-injected-row {
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            background-color: #FFFFFF !important; /* 未选中白底 */
            border: 1px solid #EAEAEA !important;
            border-radius: 6px !important;
            padding: 10px 16px !important;
            margin-bottom: 6px !important;
            box-sizing: border-box !important;
            cursor: pointer !important;
            width: 100% !important;
            height: auto !important;
          }
          #mpMv .mp-injected-row.on {
            background-color: #E8EEF8 !important; /* 选中蓝底 */
            border: 1px solid #D0D9E8 !important; /* 选中边框 */
          }
          #mpMv .mp-injected-row b {
            font-weight: normal !important; /* 防止字体太粗 */
            font-size: 14px !important;
            color: #2E3B68 !important;
            margin: 0 !important;
          }
        `;
        (document.head || document.body).appendChild(style);
      }

      // 清理原版假数据和旧数据
      mv.querySelectorAll('.mp-row, .mp-empty-row, .mp-injected-row').forEach(el => el.remove());
      
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
        emptyDiv.className = 'mp-c mp-empty-row mp-injected-row tri-preset-row';
        emptyDiv.style.cssText = "color: #7C8DB5; font-size: 13px; padding: 12px 16px; text-align: center;";
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
          // 保留原类名，同时带上 mp-injected-row 接受我们的最高权重控制
          row.className = 'mp-c mp-row mp-injected-row tri-preset-row';
          row.setAttribute('role', 'menuitemradio');
          row.setAttribute('data-m', m.name);
          
          const isActive = active && active.providerId === p.id && active.modelId === m.id;
          row.setAttribute('aria-checked', isActive ? 'true' : 'false');
          if (isActive) row.classList.add('on');
          
          const b = document.createElement('b');
          b.textContent = m.name;
          row.appendChild(b);

          // 选中时补上完美靠右的蓝色对勾
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

print("✅ 最高权重 CSS 注入完成！请运行 node --check 并 build")
