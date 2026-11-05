import sys, shutil

src = 'src/rococo_v1.js'
bak = src + '.bak_fix_input_v2'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

if '// [FIX-INPUT-V2]' in code:
    print('[skip] already patched'); sys.exit(0)

anchor = "window.__real = { chat, destroy };"
assert code.count(anchor) == 1, 'anchor hit=%d' % code.count(anchor)

patch = anchor + """
  // [FIX-INPUT-V2] 多行输入框安全重写
  setTimeout(() => {
    const oldCi = document.querySelector('.ci');
    if (!oldCi || oldCi.tagName !== 'INPUT') return;

    // 1. 创建多行文本框
    const ta = document.createElement('textarea');
    ta.className = 'ci real-ci';
    ta.id = 'ci-real';
    ta.placeholder = oldCi.getAttribute('placeholder') || '';
    ta.rows = 1;
    ta.style.cssText = 'position:absolute; left:0; top:0; width:100%; height:100%; border:0; outline:0; background:transparent; padding:0; margin:0; font-family:inherit; font-size:inherit; color:inherit; resize:none; overflow-y:hidden; line-height:1.5; z-index:10;';

    // 隐藏原版 input，并把新输入框放进去
    oldCi.style.display = 'none';
    oldCi.parentNode.insertBefore(ta, oldCi.nextSibling);

    const sync = () => {
      // 同步给原版 input，保证原有发送逻辑正常工作
      oldCi.value = ta.value;
      oldCi.dispatchEvent(new Event('input', { bubbles: true }));
      
      // 自动撑开高度
      ta.style.height = 'auto';
      ta.style.height = Math.max(24, ta.scrollHeight) + 'px';
      
      // 强制父容器也跟着变高，防止遮挡
      const ph = ta.parentNode;
      if (ph && ph.classList.contains('ph')) {
         ph.style.minHeight = ta.style.height;
      }
    };
    
    ta.addEventListener('input', sync);
    sync();

    ta.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.isComposing) {
        if (!e.shiftKey && !e.ctrlKey && !e.metaKey && !('ontouchstart' in window)) {
          e.preventDefault();
          const sendBtn = document.querySelector('.send');
          if (sendBtn) sendBtn.click();
        } else if (e.shiftKey || e.ctrlKey || e.metaKey) {
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
  }, 600);
"""

code = code.replace(anchor, patch, 1)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check]', code.count('// [FIX-INPUT-V2]'))
