import sys, shutil, re

src = 'src/rococo_v1.js'
bak = src + '.bak_fix_input_v3'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. 移除 V2 的补丁
pattern = r"  // \[FIX-INPUT-V2\][\s\S]*?window\.visualViewport\.addEventListener\('scroll', fixComposer\);\n    \}\n  \}, 600\);\n"
new_code, n = re.subn(pattern, "", code, count=1)
assert n == 1, 'remove V2 patch failed, hit=%d' % n
code = new_code

# 2. 重新注入 V3 补丁
anchor = "window.__real = { chat, destroy };"
assert code.count(anchor) == 1, 'anchor hit=%d' % code.count(anchor)

patch = anchor + """
  // [FIX-INPUT-V3] 完美还原输入框布局与换行
  setTimeout(() => {
    const oldCi = document.querySelector('.ph > input.ci');
    if (!oldCi) return;

    // 隐藏原版的占位符文字，防止重叠
    const em = document.querySelector('.ph > em');
    const pht = document.querySelector('.ph > span.pht');
    if (em) em.style.display = 'none';
    if (pht) pht.style.display = 'none';

    // 隐藏原版 input，保留给发送逻辑用
    oldCi.style.display = 'none';
    
    let ta = document.querySelector('.ph > textarea.real-ci');
    if (!ta) {
      ta = document.createElement('textarea');
      ta.className = 'ci real-ci';
      ta.rows = 1;
      ta.placeholder = '说一句话⋯';
      // 完美贴合原版排版、继承右侧留白
      ta.style.cssText = 'display:block; width:100%; min-height:22px; border:0; outline:0; background:transparent; padding:0 92px 0 0; margin:0; font-family:inherit; font-size:14.5px; font-weight:500; letter-spacing:.03em; color:#2E3A63; resize:none; overflow-y:hidden; line-height:1.5; box-sizing:border-box;';
      oldCi.parentNode.insertBefore(ta, oldCi.nextSibling);
    }

    const sync = () => {
      oldCi.value = ta.value;
      oldCi.dispatchEvent(new Event('input', { bubbles: true }));
      ta.style.height = 'auto';
      ta.style.height = Math.max(22, ta.scrollHeight) + 'px';
    };
    
    ta.addEventListener('input', sync);
    sync();

    ta.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.isComposing) {
        const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        if (!isTouch && !e.shiftKey && !e.ctrlKey && !e.metaKey) {
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

    // 修复键盘遮挡：仅使用 transform 往上推，保持水平居中不被破坏
    if (window.visualViewport) {
      const fixComposer = () => {
        const composer = document.querySelector('.composer');
        if (composer) {
          const kbHeight = window.innerHeight - window.visualViewport.height;
          if (kbHeight > 100) {
            composer.style.position = 'relative';
            composer.style.transform = 'translateY(-' + kbHeight + 'px)';
            composer.style.zIndex = '9999';
            composer.style.marginBottom = kbHeight + 'px';
          } else {
            composer.style.position = '';
            composer.style.transform = '';
            composer.style.zIndex = '';
            composer.style.marginBottom = '';
          }
        }
      };
      window.visualViewport.addEventListener('resize', fixComposer);
      window.visualViewport.addEventListener('scroll', fixComposer);
    }
  }, 800);
"""

code = code.replace(anchor, patch, 1)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check]', code.count('// [FIX-INPUT-V3]'))
