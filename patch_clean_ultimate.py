#!/usr/bin/env python3
import re, os, shutil, time, sys

p_css = 'src/rococo_v1.css'
if not os.path.exists(p_css):
    sys.exit(f"❌ 找不到 {p_css}")

# 1. 毫秒级备份
bak = f"{p_css}.bak.{int(time.time() * 1000)}"
shutil.copy2(p_css, bak)
print(f"✓ 安全备份已生成: {bak}")

s = open(p_css, encoding='utf-8').read()

# 2. 先截断旧规则
for mark in ("/* === 解除原版高度封印", "/* === 终极解封"):
    if mark in s:
        s = s.split(mark)[0]
        print(f"CSS: 已截断旧规则 {mark}")

# 3. 独立删除属性（兼容空格、换行、分号、!important 和大小写）
patterns = [
    r"\s*padding-bottom:\s*44px(\s*!important)?;?",
    r"\s*margin-bottom:\s*40px(\s*!important)?;?"
]
for pat in patterns:
    s, n = re.subn(pat, "", s, flags=re.IGNORECASE)
    print(f"CSS: 正则 {pat} → 清理 {n} 处")

# 4. 注入终极解封规则
unlock_css = """
/* === 终极解封：依靠内部内容自然撑开大框 === */
.field { height: auto !important; min-height: 0 !important; }
.field .ph { height: auto !important; }
"""
s = s.rstrip() + "\n" + unlock_css + "\n"
open(p_css, 'w', encoding='utf-8').write(s)

# 5. 终极严格回读校验
final = open(p_css, encoding='utf-8').read()
if "/* === 终极解封" not in final:
    sys.exit("❌ 校验失败：终极解封规则未写入")

# 用正则剔除所有空白字符（含空格、Tab、换行），和删除端同标准，防假阴性
compact_final = re.sub(r"\s+", "", final).lower()
if "padding-bottom:44px" in compact_final or "margin-bottom:40px" in compact_final:
    sys.exit("❌ 校验失败：发现残留的 44px 或 40px 边距！")

print("=== 完美！终极安全版（兼容 !important + 全空白校验）执行成功 ===")
