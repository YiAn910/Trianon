import sys, shutil

src = 'src/rococo_v1.js'
bak = src + '.bak_fix_input'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

if '// [FIX-INPUT]' in code:
    print('[skip] already patched'); sys.exit(0)

anchor = "window.__real = { chat, destroy };"
assert code.count(anchor) == 1, 'anchor hit=%d' % code.count(anchor)

patch = anchor + """
  // [FIX-INPUT] 替换为多行文本框，并解决软键盘遮挡
  setTimeout(() => {
    const oldCi = document.querySelector('.ci');
    if (oldCi && oldCi.tagName === 'INPUT') {
      oldCi.style.display = 'none';
      const ta = document.createElement('textarea');
      ta.className = 'real-ci';
      ta.rows = 1;
      ta.placeholder = oldCi.getAttribute('placeholder') || '';
      ta.style.cssText = 'position:absolute; left:0; top:0; width:100%; height:100%; border:0; outline:0; background:transparent; padding:0; margin:0; font-family:inherit; font-size:inherit; color:inherit; resize:none; overflow-y:hidden; line-height:1.5; z-index:10;';
      oldCi.parentNode.insertBefore(ta, oldCi.nextSibling);
      
      const sync = () => {
        oldCi.value = ta.value;
        oldCi.dispatchEvent(new Event('input', { bubbles: true }));
        ta.style.height = 'auto';
        ta.style.height = Math.max(24, ta.scrollHeight) + 'px';
      };
      ta.addEventListener('input', sync);
      
      ta.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.isComposing) {
          if (!e.shiftKey && !e.ctrlKey && !e.metaKey && !('ontouchstart' in window)) {
            // 桌面端回车发送
            e.preventDefault();
            const sendBtn = document.querySelector('.send');
            if (sendBtn) sendBtn.click();
          }
          // 移动端回车默认换行，Shift+Enter或Ctrl+Enter发送
          if (e.shiftKey || e.ctrlKey || e.metaKey) {
            e.preventDefault();
            const sendBtn = document.querySelector('.send');
            if (sendBtn) sendBtn.click();
          }
        }
      });

      if (window.visualViewport) {
        const fixComposer = () => {
          const composer = document.querySelector('.composer');
          if (composer) {
            const kbHeight = window.innerHeight - window.visualViewport.height;
            if (kbHeight > 100) {
              composer.style.position = 'fixed';
              composer.style.bottom = kbHeight + 'px';
              composer.style.left = '0';
              composer.style.right = '0';
              composer.style.zIndex = '9999';
            } else {
              composer.style.position = '';
              composer.style.bottom = '';
              composer.style.left = '';
              composer.style.right = '';
              composer.style.zIndex = '';
            }
          }
        };
        window.visualViewport.addEventListener('resize', fixComposer);
        window.visualViewport.addEventListener('scroll', fixComposer);
      }
    }
  }, 600);
"""

code = code.replace(anchor, patch, 1)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check]', code.count('// [FIX-INPUT]'))
