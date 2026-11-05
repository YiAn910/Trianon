import sys, shutil, re

src = 'src/rococo_v1.js'
bak = src + '.bak_fix_input_v4'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. 彻底清理所有残留的 FIX-INPUT 补丁
code = re.sub(r"\n  // \[FIX-INPUT.*?\}, \d+\);", "", code)
code = re.sub(r"\n  // \[FIX-INPUT-V3.*?\}, 800\);", "", code)

# 2. 注入 V4 补丁
anchor = "window.__real = { chat, destroy };"
assert code.count(anchor) == 1, 'anchor hit=%d' % code.count(anchor)

patch = anchor + """
  // [FIX-INPUT-V4] 纯净自适应多行输入框，绝不污染原版定位
  setTimeout(() => {
    const oldCi = document.querySelector('.ph > input.ci');
    if (!oldCi) return;

    // 隐藏原版的占位符文字，防止重叠
    const em = document.querySelector('.ph > em');
    const pht = document.querySelector('.ph > span.pht');
    if (em) em.style.display = 'none';
    if (pht) pht.style.display = 'none';

    if (document.querySelector('.ph > textarea.real-ci')) return;

    // 彻底隐藏原来的单行 input，保留给发送逻辑
    oldCi.style.display = 'none';

    const ta = document.createElement('textarea');
    ta.className = 'real-ci';
    ta.rows = 1;
    
    // 强制 block 流，完美继承字体、颜色，右侧留出 92px 避开按钮
    ta.style.cssText = 'position:relative; display:block; width:100%; min-height:22px; border:0; outline:0; background:transparent; margin:0; font:inherit; font-size:14.5px; font-weight:500; letter-spacing:.03em; color:#2E3A63; resize:none; overflow-y:hidden; line-height:1.5; box-sizing:border-box; padding:0 92px 0 0; z-index:10;';
    
    oldCi.parentNode.insertBefore(ta, oldCi.nextSibling);

    const sync = () => {
      // 同步数据给原版 input，激发原版的 input 事件（用于按钮高亮等）
      oldCi.value = ta.value;
      oldCi.dispatchEvent(new Event('input', { bubbles: true }));
      
      // 自适应高度
      ta.style.height = 'auto';
      ta.style.height = Math.max(22, ta.scrollHeight) + 'px';
    };
    
    ta.addEventListener('input', sync);

    // 绑定键盘：移动端回车换行；电脑端回车发送，Shift+回车换行
    ta.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.isComposing) {
        const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
        // 电脑端回车直接发送
        if (!isTouch && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
          e.preventDefault();
          const sendBtn = document.querySelector('.send');
          if (sendBtn) sendBtn.click();
        } 
        // 手动按 Shift+回车发送
        else if (e.shiftKey || e.ctrlKey || e.metaKey) {
          e.preventDefault();
          const sendBtn = document.querySelector('.send');
          if (sendBtn) sendBtn.click();
        }
      }
    });

  }, 800);
"""

code = code.replace(anchor, patch, 1)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check V4]', code.count('// [FIX-INPUT-V4]'))
print('[check V1-V3]', code.count('// [FIX-INPUT'))
