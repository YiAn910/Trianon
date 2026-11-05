import sys, shutil, re

src = 'src/rococo_v1.js'
bak = src + '.bak_rollback_input'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# 移除之前所有尝试修复输入框的补丁
code = re.sub(r"  // \[FIX-INPUT(V2|-V3)?\][\s\S]*?window\.visualViewport\.addEventListener\('scroll', fixComposer\);\n    \}\n  \}, \d+\);\n", "", code)
code = re.sub(r"  // \[FIX-INPUT\][\s\S]*?window\.visualViewport\.addEventListener\('scroll', fixComposer\);\n    \}\n  \}, 600\);\n", "", code)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] rollback done')
print('[check remaining patches]', code.count('FIX-INPUT'))
