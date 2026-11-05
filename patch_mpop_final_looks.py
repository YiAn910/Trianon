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

      // 注入专属样式，精准还原图3的浅蓝高亮和边框
      if (!document.getElementById('mp-inject-style')) {
        const style = document.createElement('style');
        style.id = 'mp-inject-style';
        style.textContent = `
          .mp-injected-row.on {
            background-color: #E8EEF8 !important;
            border: 1px solid #D0D9E8 !important;
            border-radius: 6px;
          }
        `;
        (document.head || document.documentElement).appendChild(style);
      }

      // 清理原版死数据和旧数据
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
          row.className = 'mp-c mp-row mp-injected-row tri-preset-row';
          row.setAttribute('role', 'menuitemradio');
          
          // 顺手加上图3中原版行带有的 data-m 属性
          row.setAttribute('data-m', m.name);
          
          const isActive = active && active.providerId === p.id && active.modelId === m.id;
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

print("✅ 完美外观版注入成功！请运行 node --check 并 build")
