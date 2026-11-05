#!/usr/bin/env python3
import re, os, shutil, time, sys

p_js = 'src/rococo_v1.js'
if not os.path.exists(p_js):
    sys.exit(f"❌ 找不到 {p_js}")

s = open(p_js, encoding='utf-8').read()

# 如果已经是完美的状态，直接跳过
perfect_pattern = re.compile(r"overlay\._close = null;\s*\}\s*;\s*overlay\._close = close;")
if perfect_pattern.search(s):
    print("✓ close 函数已是完美状态，无需修复。")
    sys.exit(0)

bak = f"{p_js}.bak_leak_v4.{int(time.time() * 1000)}"
shutil.copy2(p_js, bak)
print(f"✓ 安全备份: {bak}")

# 1. 遮罩点击：如果不含 _close 逻辑，则必须替换成功
onclick_pat = re.compile(
    r"(overlay\.onclick = \(e\) => \{\s*)"
    r"(if \(e\.target === overlay\) overlay\.classList\.remove\('on'\);)(\s*\}\s*;)", 
    re.S
)
s, n_onclick = onclick_pat.subn(r"\1if (e.target === overlay && overlay._close) overlay._close();\3", s, count=1)

if n_onclick > 0:
    print("JS: 遮罩点击事件接入 _close 逻辑 ✓")
elif "if (e.target === overlay && overlay._close) overlay._close();" not in s:
    sys.exit("❌ 遮罩点击锚点未找到，且未存在新逻辑，停止写入。")

# 2. 终极重写 close 函数块（修复粘连，保留完美缩进和换行）
close_pat = re.compile(
    r"([ \t]*)const close = \(\) => \{\s*"
    r"overlay\.classList\.remove\('on'\);\s*"
    r"document\.removeEventListener\('keydown', onKey\);\s*"
    r"(?:overlay\._close = null;\s*)?"
    r"\}\s*;?\s*"
    r"(?:overlay\._close = close;)?", re.S
)

def close_repl(m):
    indent = m.group(1)
    # 修复：末尾加上 \n\n{indent} 防止把后面的代码吞掉导致粘连
    return (f"{indent}const close = () => {{\n"
            f"{indent}  overlay.classList.remove('on');\n"
            f"{indent}  document.removeEventListener('keydown', onKey);\n"
            f"{indent}  overlay._close = null;\n"
            f"{indent}}};\n"
            f"{indent}overlay._close = close;\n\n{indent}")

s, n_close = close_pat.subn(close_repl, s, count=1)
if n_close == 0:
    sys.exit("❌ 未找到 close 函数块，停止写入。")
print("JS: close 函数块已完美重写（防粘连版） ✓")

# 3. 原子写入与校验
tmp_js = p_js + ".tmp"
open(tmp_js, 'w', encoding='utf-8').write(s)

final = open(tmp_js, encoding='utf-8').read()

if not perfect_pattern.search(final):
    os.remove(tmp_js)
    sys.exit(f"❌ 校验失败：最终结果没有分号或结构不对（备份 {bak}）")

# 检查是否粘连：如果 overlay._close = close; 后面紧跟着非空白字符，则说明粘连了
if re.search(r"overlay\._close = close;\S", final):
    os.remove(tmp_js)
    sys.exit("❌ 校验失败：检测到代码粘连，已放弃写入！")

if final.count("{") != final.count("}"):
    os.remove(tmp_js)
    sys.exit("❌ 校验失败：大括号数量不匹配，可能存在语法错误！")

os.replace(tmp_js, p_js)
print("=== 完美！监听器泄漏修复完成，且防粘连检查通过 ===")
