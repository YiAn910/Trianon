#!/usr/bin/env python3
import re, os, shutil, time, sys

p_js = 'src/rococo_v1.js'
if not os.path.exists(p_js):
    sys.exit(f"❌ 找不到 {p_js}")

s = open(p_js, encoding='utf-8').read()

# 检查有没有多余的“带空格空行”
# 匹配特征：overlay._close = close; 后面跟了 2 个以上换行，其中夹杂着只有空格的行
pattern = re.compile(r"(overlay\._close = close;[ \t]*\n)[\s\n]*?(?=[ \t]*const onKey)", re.S)

if pattern.search(s):
    bak = f"{p_js}.bak_blank.{int(time.time() * 1000)}"
    shutil.copy2(p_js, bak)
    
    # 替换为完美的单空行
    s = pattern.sub(r"\1\n", s)
    
    tmp_js = p_js + ".tmp"
    open(tmp_js, 'w', encoding='utf-8').write(s)
    
    final = open(tmp_js, encoding='utf-8').read()
    if final.count("{") != final.count("}"):
        os.remove(tmp_js)
        sys.exit("❌ 语法校验失败：大括号不匹配！")
        
    os.replace(tmp_js, p_js)
    print("=== 完美！多余的空行已被精准消除，代码排版如丝般顺滑 ===")
else:
    print("✓ 未发现多余的伪空行，无需清理。")
