#!/usr/bin/env python3
import re, os, shutil, time, sys

p_js = 'src/rococo_v1.js'
if not os.path.exists(p_js):
    sys.exit(f"❌ 找不到 {p_js}")

s = open(p_js, encoding='utf-8').read()

# ==========================================
# 1. 基于【特征代码】的初始状态评估
# ==========================================
has_select_new = "setProperty('user-select', 'none')" in s
has_touch_cancel = "tab.addEventListener('touchcancel', cancelPress);" in s

# 判定全局样式是否存在
guard_present = "document.getElementById('tri-del-style')" in s
inner_guard_present = bool(re.search(r"\n[ \t]{10,}if\s*\(!document\.getElementById\('tri-del-style'\)\)", s))

# 如果全部已是最新，直接退出
if has_select_new and has_touch_cancel and guard_present and not inner_guard_present:
    print("✓ 所有 UX 优化已完整存在，无需重复运行。")
    sys.exit(0)

bak = f"{p_js}.bak_ux_v8.{int(time.time() * 1000)}"
shutil.copy2(p_js, bak)
print(f"✓ 安全备份: {bak}")

# ==========================================
# 2. 清理内层冗余样式（保留缩进，非贪婪）
# ==========================================
inner_style_pattern = re.compile(
    r"\n[ \t]{10,}if\s*\(!document\.getElementById\('tri-del-style'\)\)\s*\{\s*"
    r"const\s+st\s*=\s*document\.createElement\('style'\);\s*"
    r"st\.id\s*=\s*'tri-del-style';\s*"
    r"st\.textContent\s*=\s*`[^`]+`;\s*"
    r"document\.head\.appendChild\(st\);\s*\}[ \t]*\n", re.S
)
s, clean_n = inner_style_pattern.subn("", s)
if clean_n > 0:
    print(f"JS: 已清理 {clean_n} 处内层冗余样式 ✓")

# 清理后重新评估！
guard_after_clean = "document.getElementById('tri-del-style')" in s

# ==========================================
# 3. 注入 touchcancel
# ==========================================
anchor_touchmove = r"tab\.addEventListener\('touchmove',\s*cancelPress\);"
if not has_touch_cancel:
    if re.search(anchor_touchmove, s):
        s = re.sub(anchor_touchmove, r"tab.addEventListener('touchmove', cancelPress);\n        tab.addEventListener('touchcancel', cancelPress);", s, count=1)
        print("JS: 已注入 touchcancel 监听 ✓")
    else:
        sys.exit("❌ 缺少 touchmove 锚点，放弃写入（原文件未变）")

# ==========================================
# 4. 注入防系统菜单属性
# ==========================================
if not has_select_new:
    # 兼容旧版清理
    s = re.sub(r"\n[ \t]*tab\.style\.(userSelect|webkitTouchCallout) = '(none|none)';?", "", s)
    
    # 查找准确的 tab 设置位置，防止误杀其他变量
    if s.count("tab.textContent = label;") != 1:
        sys.exit("❌ 错误：tab.textContent 锚点数量不唯一，放弃写入")
    
    # 匹配现有代码，捕获缩进
    tab_setup_pattern = re.compile(r"(tab\.textContent = label;)(\s*)(let pressTimer = null;)")
    match = tab_setup_pattern.search(s)
    if match:
        replacement = match.group(1) + "\n      tab.style.setProperty('-webkit-touch-callout', 'none');\n      tab.style.setProperty('user-select', 'none');" + match.group(2) + match.group(3)
        s = tab_setup_pattern.sub(replacement, s, count=1)
        print("JS: 已注入防系统菜单属性（保留原缩进） ✓")
    else:
        # 兜底
        s = s.replace("tab.textContent = label;", "tab.textContent = label;\n      tab.style.setProperty('-webkit-touch-callout', 'none');\n      tab.style.setProperty('user-select', 'none');", 1)
        print("JS: 已注入防系统菜单属性（兜底版） ✓")

# ==========================================
# 5. 注入全局样式（动态保留缩进）
# ==========================================
if not guard_after_clean:
    # 动态捕获 getData 前面的缩进空格
    getdata_pattern = re.compile(r"(?m)^([ \t]*)const getData = \(\) => \{")
    match = getdata_pattern.search(s)
    if match:
        indent = match.group(1)
        global_css = f"""{indent}// 注入全局样式（仅一次）
{indent}if (!document.getElementById('tri-del-style')) {{
{indent}  const st = document.createElement('style');
{indent}  st.id = 'tri-del-style';
{indent}  st.textContent = `
{indent}    .md-row .tri-del-btn {{ opacity: 0; pointer-events: none; transition: all 0.2s; }}
{indent}    .md-row:hover .tri-del-btn, .md-row.on .tri-del-btn, .md-row.kb .tri-del-btn {{ opacity: 0.5; pointer-events: auto; }}
{indent}    .tri-del-btn:hover {{ opacity: 1 !important; transform: scale(1.15) rotate(90deg); }}
{indent}    .tri-del-btn:hover svg {{ stroke: #A65B68 !important; }}
{indent}    @media (hover: none) {{
{indent}      .md-row .tri-del-btn {{ opacity: 0.3; pointer-events: auto; }}
{indent}    }}
{indent}  `;
{indent}  document.head.appendChild(st);
{indent}}}

"""
        s = s.replace(indent + "const getData = () => {", global_css + indent + "const getData = () => {", 1)
        print("JS: 全局样式注入成功（完美保留缩进） ✓")
    else:
        sys.exit("❌ 缺少 getData 锚点，放弃写入（原文件未变）")

# ==========================================
# 6. 特征校验与原子写入
# ==========================================
tmp_js = p_js + ".tmp"
open(tmp_js, 'w', encoding='utf-8').write(s)

final = open(tmp_js, encoding='utf-8').read()

if "tab.addEventListener('touchcancel', cancelPress);" not in final:
    os.remove(tmp_js)
    sys.exit(f"❌ 校验失败：touchcancel 缺失（备份 {bak}）")

if "setProperty('user-select', 'none')" not in final:
    os.remove(tmp_js)
    sys.exit(f"❌ 校验失败：user-select 缺失（备份 {bak}）")

# 检查样式守卫：必须存在且只有 1 个，且无内层缩进版
final_has_inner = bool(re.search(r"\n[ \t]{10,}if\s*\(!document\.getElementById\('tri-del-style'\)\)", final))
final_guard_count = final.count("document.getElementById('tri-del-style')")
if final_guard_count != 1 or final_has_inner:
    os.remove(tmp_js)
    sys.exit(f"❌ 校验失败：样式守卫验证未通过（出现次数 {final_guard_count}，残留内层: {final_has_inner}）")

os.replace(tmp_js, p_js)
print("=== 完美！终极无敌版 V8 执行完毕，功能与格式完美无损 ===")
