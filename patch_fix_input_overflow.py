import sys, shutil

src = 'src/rococo_v1.js'
bak = src + '.bak_fix_input_overflow'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

old_css = "      ta.style.cssText = 'position:absolute; left:0; top:0; width:100%; height:100%; border:0; outline:0; background:transparent; padding:0; margin:0; font-family:inherit; font-size:inherit; color:inherit; resize:none; overflow-y:hidden; line-height:1.5; z-index:10;';"
assert code.count(old_css) == 1, 'old_css hit=%d' % code.count(old_css)

new_css = "      ta.style.cssText = 'display:block; width:100%; min-height:24px; border:0; outline:0; background:transparent; padding:0; margin:0; font-family:inherit; font-size:inherit; color:inherit; resize:none; overflow-y:hidden; line-height:1.5; position:relative; z-index:10; box-sizing:border-box;';"
code = code.replace(old_css, new_css, 1)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check]', code.count('display:block; width:100%; min-height:24px'))
