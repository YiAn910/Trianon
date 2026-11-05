#!/usr/bin/env python3
import os, shutil, time, sys, subprocess, tempfile

ts = int(time.time() * 1000)
paths = {
    'build': 'src/build_rococo_v1.py',
    'css': 'src/rococo_v1.css',
    'js': 'src/rococo_v1.js'
}

# 1. 预检文件是否存在
for k, p in paths.items():
    if not os.path.exists(p):
        sys.exit(f"❌ 预检失败：找不到文件 {p}")

# 2. 统一备份到根目录的 patch_backups 下
os.makedirs("patch_backups", exist_ok=True)
for k, p in paths.items():
    bak = f"patch_backups/{os.path.basename(p)}.{ts}"
    shutil.copy2(p, bak)
print(f"✓ 安全备份已完成，存放于 ./patch_backups/ 下")

changes = {}

# ==========================================
# 3. 在内存中处理 build_rococo_v1.py
# ==========================================
s_build = open(paths['build'], encoding='utf-8').read()
NEW_TEXTAREA = '<textarea class="ci" id="ci" rows="1" autocomplete="off" spellcheck="false" aria-label="说一句话"></textarea>'
OLD_INPUT = '<input class="ci" id="ci" type="text" autocomplete="off" spellcheck="false" aria-label="说一句话">'

if NEW_TEXTAREA in s_build:
    print("✓ 1/3 HTML 底座：已是 textarea，跳过")
elif s_build.count(OLD_INPUT) == 1:
    s_build = s_build.replace(OLD_INPUT, NEW_TEXTAREA, 1)
    changes[paths['build']] = s_build
    print("✓ 1/3 HTML 底座：已恢复为 textarea")
else:
    sys.exit("❌ 1/3 HTML 错误：未找到完全匹配的 input 标签")

# ==========================================
# 4. 在内存中处理 rococo_v1.css
# ==========================================
s_css = open(paths['css'], encoding='utf-8').read()
OLD_CSS = ".field .ph .ci{position:absolute;left:0;top:0;width:100%;height:100%;border:0;outline:0;background:none;padding:0;margin:0;"
NEW_CSS = ".field .ph .ci{position:relative;width:100%;height:auto;min-height:22px;max-height:120px;overflow-y:auto;resize:none;border:0;outline:0;background:none;padding:0;margin:0;"
OLD_FONT = "font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;padding-right:92px;box-sizing:border-box}"
NEW_FONT = "font:inherit;font-size:14.5px;font-weight:500;letter-spacing:.03em;color:#2E3A63;caret-color:#5B6C93;padding-right:92px;box-sizing:border-box;line-height:1.5;display:block;padding-top:2px}"

if NEW_CSS in s_css and NEW_FONT in s_css:
    print("✓ 2/3 CSS 封印：已完整，跳过")
else:
    if s_css.count(OLD_CSS) == 1:
        s_css = s_css.replace(OLD_CSS, NEW_CSS, 1)
    elif NEW_CSS not in s_css:
        sys.exit("❌ 2/3 CSS 错误：未找到主规则且非新版状态")
    
    if s_css.count(OLD_FONT) == 1:
        s_css = s_css.replace(OLD_FONT, NEW_FONT, 1)
    elif NEW_FONT not in s_css:
        sys.exit("❌ 2/3 CSS 错误：未找到字体规则")
    
    changes[paths['css']] = s_css
    print("✓ 2/3 CSS 封印：已解除绝对定位并补齐字体属性")

# ==========================================
# 5. 在内存中处理 rococo_v1.js
# ==========================================
s_js = open(paths['js'], encoding='utf-8').read()
PATCH_MARK = "/* [PATCH:restore-textarea-v4] */"
ANCHOR = "ci.addEventListener('input',()=>field.classList.toggle('has',!!ci.value));"

if PATCH_MARK in s_js:
    print("✓ 3/3 JS 灵魂：撑高逻辑已存在，跳过")
else:
    if s_js.count(ANCHOR) == 1:
        inject = f"\n{PATCH_MARK}\n(()=>{{if(ci.tagName!=='TEXTAREA')return;const _sync=()=>{{if(!ci.value.trim()){{ci.style.height='22px';return;}}ci.style.height='auto';ci.style.height=Math.min(Math.max(ci.scrollHeight,22),120)+'px'}};['input','change','paste','focus'].forEach(ev=>ci.addEventListener(ev,()=>setTimeout(_sync,10)));window.addEventListener('resize',_sync);setTimeout(_sync,100);_sync()}})();"
        s_js = s_js.replace(ANCHOR, ANCHOR + inject, 1)
        changes[paths['js']] = s_js
        print("✓ 3/3 JS 灵魂：已重新注入 _sync 撑高逻辑")
    else:
        sys.exit("❌ 3/3 JS 错误：未找到唯一锚点")

# ==========================================
# 6. 统一严格校验（使用临时文件，双模式探测，完美防错杀）
# ==========================================
if paths['js'] in changes:
    def check_js(content):
        # 尝试作为 .js (CJS) 和 .mjs (ESM) 解析，两者只要过一个就不算错
        for suffix in ['.js', '.mjs']:
            fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            try:
                os.write(fd, content.encode('utf-8'))
                os.close(fd)
                r = subprocess.run(['node', '--check', tmp_path], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if r.returncode == 0:
                    return True, ""
                err_msg = r.stderr
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        return False, err_msg

    try:
        ok, err = check_js(changes[paths['js']])
        if not ok:
            sys.exit(f"❌ JS 语法错误（node --check）！\n{err}\n已终止，未覆写任何文件。")
        print("✓ 语法校验：node --check 完美通过")
    except FileNotFoundError:
        # 如果 Termux 里没装 node，则降级为局部校验注入段
        print("⚠️ 未找到 node 环境，退回局部注入段校验")
        if inject.count("{") != inject.count("}"):
            sys.exit("❌ JS 注入段括号不匹配！")

# ==========================================
# 7. 统一原子落盘
# ==========================================
if not changes:
    print("=== 检查完毕：所有文件均已是最新状态，无需改动 ===")
else:
    for p, content in changes.items():
        tmp_p = p + ".tmp"
        open(tmp_p, 'w', encoding='utf-8').write(content)
        os.replace(tmp_p, p)
    print("=== 完美！手术执行完毕，已原子写入，请执行 python build.py ===")
