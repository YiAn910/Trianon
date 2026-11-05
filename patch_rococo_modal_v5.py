#!/usr/bin/env python3
import re, os, shutil, time, sys

p_js = 'src/rococo_v1.js'
if not os.path.exists(p_js):
    sys.exit(f"❌ 找不到 {p_js}")

s = open(p_js, encoding='utf-8').read()

# 如果已经完美注入过，直接跳过
if "showRococoConfirm" in s and "overlay._close = close;" in s:
    print("✓ 完美弹窗已存在，无需重复运行。")
    sys.exit(0)

bak = f"{p_js}.bak_modal_v5.{int(time.time() * 1000)}"
shutil.copy2(p_js, bak)
print(f"✓ 安全备份: {bak}")

# ==========================================
# 1. 严格校验 getData 锚点是否唯一
# ==========================================
anchor_getdata = "const getData = () => {"
if s.count(anchor_getdata) != 1:
    sys.exit(f"❌ getData 锚点出现了 {s.count(anchor_getdata)} 次，停止写入。")

match = re.search(r"(?m)^([ \t]*)const getData = \(\) => \{", s)
indent = match.group(1) if (match and match.group(1)) else "  "

# ==========================================
# 2. 定义最完美的弹窗代码（含无泄漏 close、ESC、完美排版）
# ==========================================
modal_code = f"""{indent}// === 洛可可自定义确认弹窗（Global） ===
{indent}if (!document.getElementById('rococo-confirm-style')) {{
{indent}  const st = document.createElement('style');
{indent}  st.id = 'rococo-confirm-style';
{indent}  st.textContent = `
{indent}    .rococo-confirm-overlay {{
{indent}      position: fixed; inset: 0;
{indent}      background: rgba(230, 235, 245, 0.45);
{indent}      backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
{indent}      z-index: 999999;
{indent}      display: flex; align-items: center; justify-content: center;
{indent}      opacity: 0; pointer-events: none;
{indent}      transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
{indent}    }}
{indent}    .rococo-confirm-overlay.on {{ opacity: 1; pointer-events: auto; }}
{indent}    .rococo-confirm-box {{
{indent}      background: #FBFCFE;
{indent}      border-radius: 16px;
{indent}      padding: 28px 32px;
{indent}      box-shadow: 0 16px 40px rgba(46, 59, 104, 0.15), 0 0 0 1px rgba(124, 141, 181, 0.2);
{indent}      width: 90%; max-width: 380px;
{indent}      text-align: center;
{indent}      transform: translateY(20px) scale(0.95);
{indent}      transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
{indent}      position: relative;
{indent}      overflow: hidden;
{indent}    }}
{indent}    .rococo-confirm-box::before {{
{indent}      content: ""; position: absolute; inset: 0;
{indent}      border: 1px dashed rgba(124, 141, 181, 0.3);
{indent}      border-radius: inherit; pointer-events: none;
{indent}      margin: 6px;
{indent}    }}
{indent}    .rococo-confirm-overlay.on .rococo-confirm-box {{ transform: translateY(0) scale(1); }}
{indent}    .rococo-confirm-title {{
{indent}      font-size: 18px; font-weight: 600; color: #2E3A63;
{indent}      margin-bottom: 12px; letter-spacing: 0.05em;
{indent}      font-family: "Cormorant Garamond", "Noto Serif CJK SC", serif;
{indent}    }}
{indent}    .rococo-confirm-msg {{
{indent}      font-size: 14.5px; color: #5B6C93; margin-bottom: 24px;
{indent}      line-height: 1.6; padding: 0 10px;
{indent}    }}
{indent}    .rococo-confirm-actions {{
{indent}      display: flex; gap: 16px; justify-content: center;
{indent}    }}
{indent}    .rococo-confirm-btn {{
{indent}      padding: 8px 24px; border-radius: 8px; font-size: 14px; font-weight: 500;
{indent}      cursor: pointer; transition: all 0.2s; user-select: none;
{indent}      font-family: inherit; letter-spacing: 0.05em;
{indent}    }}
{indent}    .rococo-confirm-cancel {{
{indent}      background: transparent; border: 1px solid rgba(124, 141, 181, 0.4);
{indent}      color: #7C8DB5;
{indent}    }}
{indent}    .rococo-confirm-cancel:hover {{ background: rgba(124, 141, 181, 0.08); color: #2E3A63; border-color: #2E3A63; }}
{indent}    .rococo-confirm-ok {{
{indent}      background: #5B6C93; border: 1px solid #5B6C93; color: #FFFFFF;
{indent}      box-shadow: 0 4px 12px rgba(91, 108, 147, 0.25);
{indent}    }}
{indent}    .rococo-confirm-ok:hover {{ background: #2E3A63; border-color: #2E3A63; transform: translateY(-1px); box-shadow: 0 6px 16px rgba(91, 108, 147, 0.35); }}
{indent}  `;
{indent}  document.head.appendChild(st);
{indent}}}

{indent}function showRococoConfirm(msg, onConfirm) {{
{indent}  let overlay = document.getElementById('rococo-confirm-overlay');
{indent}  if (!overlay) {{
{indent}    overlay = document.createElement('div');
{indent}    overlay.id = 'rococo-confirm-overlay';
{indent}    overlay.className = 'rococo-confirm-overlay';
{indent}    overlay.innerHTML = `
{indent}      <div class="rococo-confirm-box">
{indent}        <div class="rococo-confirm-title">确认操作</div>
{indent}        <div class="rococo-confirm-msg"></div>
{indent}        <div class="rococo-confirm-actions">
{indent}          <div class="rococo-confirm-btn rococo-confirm-cancel">取消</div>
{indent}          <div class="rococo-confirm-btn rococo-confirm-ok">确定</div>
{indent}        </div>
{indent}      </div>
{indent}    `;
{indent}    document.body.appendChild(overlay);
{indent}    overlay.onclick = (e) => {{
{indent}      if (e.target === overlay && overlay._close) overlay._close();
{indent}    }};
{indent}  }}

{indent}  const msgEl = overlay.querySelector('.rococo-confirm-msg');
{indent}  const btnCancel = overlay.querySelector('.rococo-confirm-cancel');
{indent}  const btnOk = overlay.querySelector('.rococo-confirm-ok');

{indent}  msgEl.textContent = msg;

{indent}  const onKey = (e) => {{
{indent}    if (e.key === 'Escape') {{
{indent}      e.preventDefault();
{indent}      if (overlay._close) overlay._close();
{indent}    }}
{indent}  }};

{indent}  const close = () => {{
{indent}    overlay.classList.remove('on');
{indent}    document.removeEventListener('keydown', onKey);
{indent}    overlay._close = null;
{indent}  }};
{indent}  overlay._close = close;

{indent}  document.addEventListener('keydown', onKey);

{indent}  btnCancel.onclick = (e) => {{ e.stopPropagation(); close(); }};
{indent}  btnOk.onclick = (e) => {{ 
{indent}    e.stopPropagation(); 
{indent}    close(); 
{indent}    if (onConfirm) onConfirm(); 
{indent}  }};

{indent}  setTimeout(() => {{ overlay.classList.add('on'); }}, 10);
{indent}}}

"""

s = s.replace(anchor_getdata, modal_code + anchor_getdata, 1)
print("JS: 完美的洛可可弹窗底层代码已注入 ✓")

# ==========================================
# 3. 替换两处原生 confirm
# ==========================================
# 3.1 Tab 删除确认
old_tab_block = """          if (confirm('确定要删除预设「' + label + '」以及其下所有模型吗？')) {
            isLongPress = true; // 【修复】仅在确认删除时才拦截点击
            const newData = getData();
            newData.providers = newData.providers.filter(x => x.id !== id);
            if (newData.activeModel && newData.activeModel.providerId === id) {
              newData.activeModel = null;
            }
            saveData(newData);
            if (currentTabId === id) currentTabId = 'all';
            renderCatalogueFn();
          }"""
new_tab_block = """          showRococoConfirm('确定要删除预设「' + label + '」以及其下所有模型吗？', () => {
            isLongPress = true; // 【修复】仅在确认删除时才拦截点击
            const newData = getData();
            newData.providers = newData.providers.filter(x => x.id !== id);
            if (newData.activeModel && newData.activeModel.providerId === id) {
              newData.activeModel = null;
            }
            saveData(newData);
            if (currentTabId === id) currentTabId = 'all';
            renderCatalogueFn();
          });"""
if old_tab_block in s:
    s = s.replace(old_tab_block, new_tab_block, 1)
    print("JS: Tab 删除确认已替换为洛可可弹窗 ✓")
else:
    sys.exit("❌ Tab 删除锚点未找到（原文件未变）")

# 3.2 模型删除确认
old_mdl_block = """                if (confirm('确定要删除模型：' + m.name + ' 吗？')) {
                  const newData = getData();
                  const pr = newData.providers.find(x => x.id === p.id);
                  if (pr) {
                    pr.models = pr.models.filter(mm => mm.id !== m.id);
                    if (newData.activeModel && newData.activeModel.providerId === p.id && newData.activeModel.modelId === m.id) {
                      newData.activeModel = null;
                    }
                    saveData(newData);
                    if (typeof renderCatalogueFn === 'function') renderCatalogueFn();
                  }
                }"""
new_mdl_block = """                showRococoConfirm('确定要删除模型：' + m.name + ' 吗？', () => {
                  const newData = getData();
                  const pr = newData.providers.find(x => x.id === p.id);
                  if (pr) {
                    pr.models = pr.models.filter(mm => mm.id !== m.id);
                    if (newData.activeModel && newData.activeModel.providerId === p.id && newData.activeModel.modelId === m.id) {
                      newData.activeModel = null;
                    }
                    saveData(newData);
                    if (typeof renderCatalogueFn === 'function') renderCatalogueFn();
                  }
                });"""
if old_mdl_block in s:
    s = s.replace(old_mdl_block, new_mdl_block, 1)
    print("JS: 模型删除确认已替换为洛可可弹窗 ✓")
else:
    sys.exit("❌ 模型删除锚点未找到（原文件未变）")

# ==========================================
# 4. 原子写入与校验
# ==========================================
tmp_js = p_js + ".tmp"
open(tmp_js, 'w', encoding='utf-8').write(s)

final = open(tmp_js, encoding='utf-8').read()

# 精确校验
if "confirm('确定要删除预设" in final or "confirm('确定要删除模型" in final:
    os.remove(tmp_js)
    sys.exit(f"❌ 校验失败：发现了残留的旧 confirm（备份 {bak}）")

if final.count("showRococoConfirm") != 3:
    os.remove(tmp_js)
    sys.exit(f"❌ 校验失败：showRococoConfirm 出现次数为 {final.count('showRococoConfirm')}，应为 3（备份 {bak}）")

# 检查粘连
if re.search(r"overlay\._close = close;\S", final):
    os.remove(tmp_js)
    sys.exit("❌ 校验失败：检测到代码粘连，已放弃写入！")

if final.count("{") != final.count("}"):
    os.remove(tmp_js)
    sys.exit("❌ 校验失败：大括号数量不匹配！")

os.replace(tmp_js, p_js)
print("=== 完美！洛可可弹窗 V5（防泄漏 + 防粘连 + 强校验）已写入 ===")
