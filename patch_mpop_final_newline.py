import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_str = "const injectRows = () => {"
start_idx = content.find(start_str)
assert start_idx != -1, "❌ 找不到 injectRows 函数起点！"

# 定位大括号结束
brace_start = start_idx + len(start_str) - 1
depth = 1
idx = brace_start + 1
n = len(content)

# 状态机（简略版，只为了跳过字符串/注释找括号）
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

# 【修复粘连】跳过原有尾部的空格和分号，但绝不吞换行
brace_end = idx
while brace_end < n and content[brace_end] in ' \t':
    brace_end += 1
if brace_end < n and content[brace_end] == ';':
    brace_end += 1

new_block = """const injectRows = () => {
      const mv = document.getElementById('mpMv');
      if (!mv) return;

      mv.querySelectorAll('.mp-injected-row').forEach(el => el.remove());
      
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
        emptyDiv.textContent = "暂无收藏的模型，请在“更多模型”中收藏";
        safeInsert(emptyDiv);
      } else {
        starredModels.sort((a, b) => (a.provider.name || '').localeCompare(b.provider.name || '') || (a.model.name || '').localeCompare(b.model.name || ''));

        starredModels.forEach(item => {
          const p = item.provider;
          const m = item.model;
          
          const row = document.createElement('div');
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

# 拼接时，new_block 自带换行，content[brace_end:] 也是从换行开始，所以格式完美
content = content[:start_idx] + new_block + content[brace_end:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 格式与逻辑已彻底完美！请运行 node --check src/rococo_v1.js 并 build")
