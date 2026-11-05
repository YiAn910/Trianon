import os

file_path = 'src/rococo_v1.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_str = "const injectRows = () => {"
start_idx = content.find(start_str)

assert start_idx != -1, "❌ 找不到 injectRows 函数起点！"
# 【修复低隐患】检查是否有重复定义
assert content.find(start_str, start_idx + 1) == -1, "❌ 发现多个 injectRows 定义，请先清理残留！"

# 【终极定位算法】词法分析状态机：跳过字符串、注释、模板字面量
brace_start = start_idx + len(start_str) - 1
depth = 1
idx = brace_start + 1
n = len(content)

in_single_quote = False
in_double_quote = False
in_template_quote = False
in_single_comment = False
in_multi_comment = False

while idx < n and depth > 0:
    char = content[idx]
    next_char = content[idx+1] if idx+1 < n else ''
    
    if in_single_comment:
        if char == '\n': in_single_comment = False
        idx += 1; continue
    if in_multi_comment:
        if char == '*' and next_char == '/':
            in_multi_comment = False
            idx += 2; continue
        idx += 1; continue
        
    if in_single_quote:
        if char == '\\':
            idx += 2; continue
        if char == "'": in_single_quote = False
        idx += 1; continue
    if in_double_quote:
        if char == '\\':
            idx += 2; continue
        if char == '"': in_double_quote = False
        idx += 1; continue
    if in_template_quote:
        if char == '\\':
            idx += 2; continue
        if char == '`': in_template_quote = False
        # 模板字符串中的 ${ 属于括号嵌套，这里保持正常扫描
        idx += 1; continue

    if char == '/' and next_char == '/':
        in_single_comment = True; idx += 2; continue
    if char == '/' and next_char == '*':
        in_multi_comment = True; idx += 2; continue
        
    if char == "'": in_single_quote = True; idx += 1; continue
    if char == '"': in_double_quote = True; idx += 1; continue
    if char == '`': in_template_quote = True; idx += 1; continue

    if char == '{': depth += 1
    elif char == '}': depth -= 1
    idx += 1

assert depth == 0, "❌ 大括号未闭合，找不到函数终点！"

# 【修复双分号】跳过紧随其后的分号和空白
brace_end = idx
while brace_end < n and content[brace_end] in ' \t\r\n;':
    brace_end += 1

new_block = """const injectRows = () => {
      const mv = document.getElementById('mpMv');
      if (!mv) return;

      // 只清理自己生成的元素
      mv.querySelectorAll('.mp-injected-row').forEach(el => el.remove());
      
      const data = getData();
      const active = data.activeModel;
      
      // 条件覆盖 targetNode
      const header = mv.querySelector('.mp-hd');
      let targetNode = header ? header.nextElementSibling : mv.firstElementChild;
      
      const allDivs = Array.from(mv.querySelectorAll('div'));
      const moreDiv = allDivs.find(el => el.textContent.includes('更多模型') && el.children.length === 0);
      
      // 【修复 Bug1】排除 moreDiv.parentNode === mv 的情况
      if (moreDiv && moreDiv.parentNode && moreDiv.parentNode !== mv) {
        const moreParent = moreDiv.parentNode;
        // 【修复 Bug1】排除 targetNode === mv 的情况
        const tgtOk = targetNode && mv.contains(targetNode) && targetNode !== mv;
        const tgtAfterMore = tgtOk && (moreParent.compareDocumentPosition(targetNode) & Node.DOCUMENT_POSITION_FOLLOWING);
        if (!tgtOk || tgtAfterMore) {
          targetNode = moreParent;
        }
      }

      // 【修复 Bug1】safeInsert 增加 targetNode !== mv 保护
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
    };"""

content = content[:start_idx] + new_block + content[brace_end:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 完美无瑕版注入成功！请运行 node --check src/rococo_v1.js")
