import sys, shutil, re

src = 'src/rococo_v1.js'
bak = src + '.bak_fix_input_v11'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

if '// [FIX-INPUT-V11] START' in code:
    print('[skip] already patched'); sys.exit(0)

# 1. 利用显式标记清理 V10
code = re.sub(r"\n  // \[FIX-INPUT-V10\] START[\s\S]*?// \[FIX-INPUT-V10\] END\n", "", code)
# 顺手补齐 V1-V7 的清理，防止跨版本残留
code = re.sub(r"\n  // \[FIX-INPUT-V[1-8]\][\s\S]*?\n  \}\)\(\);", "", code)
code = re.sub(r"\n  // \[FIX-INPUT-V[1-7]\][\s\S]*?\n  \}, \d+\);", "", code)

# 2. 注入 V11
anchor = "window.__real = { chat, destroy };"
assert code.count(anchor) == 1, 'anchor hit=%d' % code.count(anchor)

patch = anchor + """
  // [FIX-INPUT-V11] START
  (function initMultilineInput() {
    if (!document.getElementById('fix-ph-css')) {
      const style = document.createElement('style');
      style.id = 'fix-ph-css';
      style.textContent = `
        .field .ph { height: auto !important; min-height: 30px; }
        .field .ph > em, .field .ph > .pht { display: none !important; }
        /* 92px 给右侧绝对定位的模型选择器留位 */
        .field .ph > textarea.real-ci { padding-right: 92px !important; }
      `;
      document.head.appendChild(style);
    }

    // 假设当前页面只有一个主输入区 .ph
    const injectTextarea = () => {
      const oldCi = document.querySelector('.ph > input.ci');
      if (!oldCi) return;

      // 全局清理旧 textarea，清理 observer 防泄漏
      const prevTa = document.querySelector('textarea.real-ci');
      if (prevTa) {
        if (prevTa.__phtMo) {
          prevTa.__phtMo.disconnect();
          prevTa.__phtMo = null;
        }
        prevTa.remove();
      }

      oldCi.style.display = 'none';

      const ta = document.createElement('textarea');
      ta.className = 'ci real-ci';
      ta.rows = 1;
      
      const updatePlaceholder = () => {
        const pht = document.querySelector('.ph > .pht, .ph > em');
        const text = oldCi.getAttribute('placeholder') || (pht ? pht.textContent.trim() : '');
        if (ta.placeholder !== text) ta.placeholder = text;
      };
      updatePlaceholder();
      
      const phEl = document.querySelector('.ph');
      if (phEl && window.MutationObserver) {
        const phtMo = new MutationObserver(updatePlaceholder);
        phtMo.observe(phEl, { characterData: true, childList: true, subtree: true });
        ta.__phtMo = phtMo;
      }
      
      ta.style.cssText = 'display:block; width:100%; min-height:22px; border:0; outline:0; background:transparent; margin:0; font-family:inherit; font-size:14.5px; font-weight:500; letter-spacing:.03em; color:#2E3A63; resize:none; overflow-y:hidden; line-height:1.5; box-sizing:border-box; padding:0;';
      
      oldCi.parentNode.insertBefore(ta, oldCi.nextSibling);

      // 修复 focus 监听器累积泄漏：全局只挂载一次，且不持有 ta 闭包
      if (!oldCi.__focusRedirect) {
        oldCi.addEventListener('focus', () => {
          const cur = document.querySelector('.ph > textarea.real-ci');
          if (cur) cur.focus();
        });
        oldCi.__focusRedirect = true;
      }

      const sync = () => {
        oldCi.value = ta.value;
        oldCi.dispatchEvent(new Event('input', { bubbles: true }));
        ta.style.height = 'auto';
        ta.style.height = Math.max(22, ta.scrollHeight) + 'px';
      };

      const proto = HTMLInputElement.prototype;
      const desc = Object.getOwnPropertyDescriptor(proto, 'value');
      if (desc && desc.set) {
        Object.defineProperty(oldCi, 'value', {
          configurable: true,
          get() { return desc.get ? desc.get.call(this) : ''; },
          set(v) {
            desc.set.call(this, v);
            if (v === '' && ta.value !== '') {
              ta.value = '';
              ta.style.height = 'auto';
              ta.style.height = Math.max(22, ta.scrollHeight) + 'px';
            }
          }
        });
      }

      ta.value = oldCi.value || '';
      sync();
      
      ta.addEventListener('input', sync);

      // 修复中文输入法 compositionend 后误发
      let composing = false;
      ta.addEventListener('compositionstart', () => composing = true);
      ta.addEventListener('compositionend', () => setTimeout(() => composing = false, 0));

      ta.addEventListener('keydown', (e) => {
        if (e.key !== 'Enter' || composing || e.isComposing) return;

        const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        if (isTouch) return;                
        if (e.shiftKey || e.altKey) return; 
        
        e.preventDefault();
        const sendBtn = document.querySelector('.send');
        if (sendBtn) sendBtn.click();
      });
    };

    let pending = false;
    const mo = new MutationObserver(() => {
      if (document.querySelector('.ph > textarea.real-ci')) return;
      if (pending) return;
      pending = true;
      requestAnimationFrame(() => {
        injectTextarea();
        pending = false;
      });
    });
    mo.observe(document.body, { childList: true, subtree: true });
    
    // 首屏加早退判断，防止热重载时的 DOM 抖动
    if (!document.querySelector('.ph > textarea.real-ci')) {
      injectTextarea();
    }
  })();
  // [FIX-INPUT-V11] END
"""

code = code.replace(anchor, patch, 1)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check V11]', code.count('// [FIX-INPUT-V11] START'))
