#!/usr/bin/env python3
import re, os, shutil, time, sys

p_js = 'src/rococo_v1.js'
if not os.path.exists(p_js):
    sys.exit(f"❌ 找不到 {p_js}")

s = open(p_js, encoding='utf-8').read()

INJECT_MARK = "/* [PATCH:delete-v10] */"
if INJECT_MARK in s:
    print("✓ 补丁已完整存在，无需重复注入。")
    sys.exit(0)

bak = f"{p_js}.bak_delv10.{int(time.time() * 1000)}"
shutil.copy2(p_js, bak)
print(f"✓ 安全备份: {bak}")

# ==========================================
# 1. 替换 createTab：注入长按删除 + 移动端防误触
# ==========================================
old_tab = """      const createTab = (id, label) => {
        const tab = document.createElement('div');
        tab.className = 'ptab' + (currentTabId === id ? ' on' : '');
        tab.textContent = label;
        tab.onclick = () => { currentTabId = id; renderCatalogueFn(); };
        mdTabs.appendChild(tab);
      };"""

new_tab = """      const createTab = (id, label) => {
        const tab = document.createElement('div');
        tab.className = 'ptab' + (currentTabId === id ? ' on' : '');
        tab.textContent = label;
        
        tab.style.setProperty('-webkit-touch-callout', 'none');
        tab.style.setProperty('user-select', 'none');
        
        let pressTimer = null;
        let isLongPress = false;
        const startPress = () => {
          isLongPress = false;
          pressTimer = setTimeout(() => {
            if (confirm('确定要删除预设「' + label + '」以及其下所有模型吗？')) {
              isLongPress = true;
              const newData = getData();
              newData.providers = newData.providers.filter(x => x.id !== id);
              if (newData.activeModel && newData.activeModel.providerId === id) {
                newData.activeModel = null;
              }
              saveData(newData);
              if (currentTabId === id) currentTabId = 'all';
              renderCatalogueFn();
            }
          }, 600);
        };
        const cancelPress = () => { if (pressTimer) clearTimeout(pressTimer); };
        
        if (id !== 'all') {
          tab.addEventListener('touchstart', startPress, {passive: true});
          tab.addEventListener('touchend', cancelPress);
          tab.addEventListener('touchmove', cancelPress);
          tab.addEventListener('touchcancel', cancelPress);
          tab.addEventListener('mousedown', startPress);
          tab.addEventListener('mouseup', cancelPress);
          tab.addEventListener('mouseleave', cancelPress);
        }
        
        tab.onclick = (e) => {
          if (isLongPress) { e.stopPropagation(); e.preventDefault(); return; }
          currentTabId = id; renderCatalogueFn();
        };
        mdTabs.appendChild(tab);
      };"""

if s.count(old_tab) != 1:
    sys.exit("❌ 错误：找不到原始 createTab 锚点，放弃写入。")
s = s.replace(old_tab, new_tab, 1)
print("JS: Tab 长按删除及防误触已注入 ✓")

# ==========================================
# 2. 模型列表：注入删除按钮（精准锚点版）
# ==========================================
old_mdl = """              actionDiv.appendChild(starBtn);
            }
            row.appendChild(actionDiv);"""

new_mdl = """              actionDiv.appendChild(starBtn);
            }
            
            if (!document.getElementById('tri-del-style')) {
              const st = document.createElement('style');
              st.id = 'tri-del-style';
              st.textContent = `
                .md-row .tri-del-btn { opacity: 0; pointer-events: none; transition: all 0.2s; }
                .md-row:hover .tri-del-btn, .md-row.on .tri-del-btn, .md-row.kb .tri-del-btn { opacity: 0.5; pointer-events: auto; }
                .tri-del-btn:hover { opacity: 1 !important; transform: scale(1.15) rotate(90deg); }
                .tri-del-btn:hover svg { stroke: #A65B68 !important; }
                @media (hover: none) {
                  .md-row .tri-del-btn { opacity: 0.3; pointer-events: auto; }
                }
              `;
              document.head.appendChild(st);
            }

            const delBtn = document.createElement('div');
            delBtn.className = 'tri-del-btn';
            delBtn.style.cssText = 'cursor: pointer; display: flex; align-items: center; justify-content: center; width: 20px; height: 20px; margin-left: 8px;';
            delBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="#7C8DB5" stroke-width="1.2" stroke-linecap="round"><path d="M2,2 L10,10 M10,2 L2,10"/></svg>';
            
            delBtn.onclick = (ev) => {
              ev.stopPropagation();
              if (confirm('确定要删除模型：' + m.name + ' 吗？')) {
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
              }
            };
            actionDiv.appendChild(delBtn);
            
            row.appendChild(actionDiv);"""

if s.count(old_mdl) != 1:
    sys.exit("❌ 错误：找不到 actionDiv 锚点，放弃写入。")
s = s.replace(old_mdl, new_mdl, 1)
print("JS: 模型列表删除按钮已注入 ✓")

# ==========================================
# 3. 预设列表：注入取消收藏按钮
# ==========================================
old_mp = """          ckSvg.appendChild(ckPath);
          row.appendChild(ckSvg);

          // 原生点击逻辑"""

new_mp = """          ckSvg.appendChild(ckPath);
          row.appendChild(ckSvg);

          const delPresetBtn = document.createElement('div');
          delPresetBtn.className = 'tri-del-btn-preset';
          delPresetBtn.style.cssText = 'margin-left: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 18px; height: 18px; opacity: 0.3; transition: all 0.2s;';
          delPresetBtn.innerHTML = '<svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="#7C8DB5" stroke-width="1.2" stroke-linecap="round"><path d="M2,2 L10,10 M10,2 L2,10"/></svg>';
          delPresetBtn.onmouseenter = () => { delPresetBtn.style.opacity = '1'; delPresetBtn.style.transform = 'rotate(90deg)'; delPresetBtn.querySelector('svg').setAttribute('stroke', '#A65B68'); };
          delPresetBtn.onmouseleave = () => { delPresetBtn.style.opacity = '0.3'; delPresetBtn.style.transform = 'none'; delPresetBtn.querySelector('svg').setAttribute('stroke', '#7C8DB5'); };
          
          delPresetBtn.onclick = (ev) => {
            ev.stopPropagation();
            const newData = getData();
            const pr = newData.providers.find(x => x.id === p.id);
            if (pr) {
              const mm = pr.models.find(x => x.id === m.id);
              if (mm) {
                mm.starred = false;
                saveData(newData);
                if (typeof injectRows === 'function') injectRows();
              }
            }
          };
          row.appendChild(delPresetBtn);

          // 原生点击逻辑"""

if s.count(old_mp) != 1:
    sys.exit("❌ 错误：找不到预设列表锚点，放弃写入。")
s = s.replace(old_mp, new_mp, 1)
print("JS: 预设列表取消收藏已注入 ✓")

# 添加统一的 PATCH 标记
s = s.replace("  // ================= 数据结构与存储 =================", f"  {INJECT_MARK}\n  // ================= 数据结构与存储 =================", 1)

# ==========================================
# 4. 原子写入与校验
# ==========================================
tmp_js = p_js + ".tmp"
open(tmp_js, 'w', encoding='utf-8').write(s)

final = open(tmp_js, encoding='utf-8').read()

if INJECT_MARK not in final or "tri-del-btn" not in final or "touchcancel" not in final:
    os.remove(tmp_js)
    sys.exit(f"❌ 校验失败，已放弃写入（原文件未变，备份 {bak}）")

os.replace(tmp_js, p_js)
print("=== 完美！V10 一次性注入成功，所有功能已就位 ===")
