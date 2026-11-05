import sys, shutil

src = 'src/rococo_v1.js'
bak = src + '.bak_force_real_mode'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

if "setItem('trianon_mode','real')" in code:
    print('[skip] already patched'); sys.exit(0)

anchor = "window.__real = { chat, destroy };"
assert code.count(anchor) == 1, 'anchor hit=%d' % code.count(anchor)

insert = (
    "window.__real = { chat, destroy };\n"
    "  // [FORCE-REAL] 强制走真实请求分支，避免新环境 localStorage 空导致默认 Demo\n"
    "  try { localStorage.setItem('trianon_mode', 'real'); } catch (e) {}\n"
)
code = code.replace(anchor, insert, 1)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check]', code.count("setItem('trianon_mode','real')"))
