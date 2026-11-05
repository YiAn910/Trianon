#!/usr/bin/env python3
import re, os, shutil, time, sys

p_js = 'src/rococo_v1.js'
if not os.path.exists(p_js):
    sys.exit(f"❌ 找不到 {p_js}")

# 毫秒级备份
bak = f"{p_js}.bak_del.{int(time.time() * 1000)}"
shutil.copy2(p_js, bak)
print(f"✓ 安全备份: {bak}")

s = open(p_js, encoding='utf-8').read()

# ==========================================
# 1. 修改 createTab：支持长按删除预设（API）
# ==========================================
old_tab_pat = re.compile(
    r"const createTab = \(id, label\) => \{\s*"
    r"const tab = document\.createElement\('div'\);\s*"
    r"tab\.className = 'ptab' \+ \(currentTabId === id \? ' on' : ''\);\s*"
    r"tab\.textContent = label;\s*"
    r"tab\.onclick = \(\) => \{ currentTabId = id; renderCatalogueFn\(\); \};\s*"
    r"mdTabs\.appendChild\(tab\);\s*\}", re.S
)

new_tab_code = """const createTab = (id, label) => {
      const tab = document.createElement('div');
      tab.className = 'ptab' + (currentTabId === id ? ' on' : '');
      tab.textContent = label;
      
      let pressTimer = null;
      let isLongPress = false;
      const startPress = () => {
        isLongPress = false;
        pressTimer = setTimeout(() => {
          isLongPress = true;
          if (confirm('确定要删除预设「' + label + '」以及其下所有模型吗？')) {
            const newData = getData();
            newData.providers = newData.providers.filter(x => x.id !== id);
            if (newData.activeModel && newData.activeModel.providerId === id) {
              newData.activeModel = null;
            }
            saveData(newData);
            currentTabId = 'all';
            renderCatalogueFn();
          }
        }, 600);
      };
      const cancelPress = () => { if (pressTimer) clearTimeout(pressTimer); };
      
      if (id !== 'all') {
        tab.addEventListener('touchstart', startPress, {passive: true});
        tab.addEventListener('touchend', cancelPress);
        tab.addEventListener('touchmove', cancelPress);
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

s, n = old_tab_pat.subn(new_tab_code, s, count=1)
if n == 0: sys.exit("❌ createTab 锚点未找到，停止写入（原文件未动）")
print("JS: Tab 长按删除预设逻辑已注入 ✓")

# ==========================================
# 2. 模型列表：在 actionDiv 中注入和星星同显隐的 X
# ==========================================
# 找到 if (isActive || m.starred) 块结束的地方，注入全局 CSS 和 delBtn
old_mdl_tail = """              if (isActive || m.starred) {
                actionDiv.appendChild(starBtn);
              }
            }"""
new_mdl_tail = """              if (isActive || m.starred) {
                actionDiv.appendChild(starBtn);
              }
              
              // === 注入洛可可风删除按钮（管理页，默认隐，hover/选中现） ===
              if (!document.getElementById('tri-del-style')) {
                const st = document.createElement('style');
                st.id = 'tri-del-style';
                st.textContent = `
                  .md-row .tri-del-btn { opacity: 0 !important; pointer-events: none; transition: all 0.2s; }
                  .md-row:hover .tri-del-btn, .md-row.on .tri-del-btn, .md-row.kb .tri-del-btn { opacity: 0.5 !important; pointer-events: auto; }
                  .tri-del-btn:hover { opacity: 1 !important; transform: scale(1.15) rotate(90deg); }
                  .tri-del-btn:hover svg { stroke: #A65B68 !important; }
                `;
                document.head.appendChild(st);
              }

              const delBtn = document.createElement('div');
              delBtn.className = 'tri-del-btn';
              delBtn.style.cssText = 'cursor: pointer; display: flex; align-items: center; justify-content: center; width: 20px; height: 20px; margin-left: 8px;';
              delBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="#7C8DB5" stroke-width="1.2" stroke-linecap="round"><path d="M2,2 L10,10 M10,2 L2,10"/></svg>';
              
              delBtn.onclick = (ev) => {
                ev.stopPropagation(); // 阻止选中
                if (confirm('确定要删除模型：' + m.name + ' 吗？')) {
                  const newData = getData();
                  const pr = newData.providers.find(x => x.id === p.id);
                  if (pr) {
                    pr.models = pr.models.filter(mm => mm.id !== m.id);
                    saveData(newData);
                    if (typeof renderCatalogueFn === 'function') renderCatalogueFn();
                  }
                }
              };
              actionDiv.appendChild(delBtn);
            }"""

if s.count(old_mdl_tail) != 1:
    sys.exit("❌ 模型列表 actionDiv 锚点未唯一找到（原文件未动）")
s = s.replace(old_mdl_tail, new_mdl_tail, 1)
print("JS: 模型列表删除按钮已注入 ✓")

# ==========================================
# 3. 预设列表：给 row 注入极简 X
# ==========================================
old_mp_tail = """          ckSvg.appendChild(ckPath);
          row.appendChild(ckSvg);

          // 原生点击逻辑"""

new_mp_tail = """          ckSvg.appendChild(ckPath);
          row.appendChild(ckSvg);

          // === 注入洛可可风删除按钮（预设页，取消收藏） ===
          const delPresetBtn = document.createElement('div');
          delPresetBtn.className = 'tri-del-btn-preset';
          delPresetBtn.style.cssText = 'margin-left: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 18px; height: 18px; opacity: 0.3; transition: all 0.2s;';
          delPresetBtn.innerHTML = '<svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="#7C8DB5" stroke-width="1.2" stroke-linecap="round"><path d="M2,2 L10,10 M10,2 L2,10"/></svg>';
          delPresetBtn.onmouseenter = () => { delPresetBtn.style.opacity = '1'; delPresetBtn.style.transform = 'rotate(90deg)'; delPresetBtn.querySelector('svg').setAttribute('stroke', '#A65B68'); };
          delPresetBtn.onmouseleave = () => { delPresetBtn.style.opacity = '0.3'; delPresetBtn.style.transform = 'none'; delPresetBtn.querySelector('svg').setAttribute('stroke', '#7C8DB5'); };
          
          delPresetBtn.onclick = (ev) => {
            ev.stopPropagation(); // 阻止选中
            const newData = getData();
            const pr = newData.providers.find(x => x.id === p.id);
            if (pr) {
              const mm = pr.models.find(x => x.id === m.id);
              if (mm) {
                mm.starred = false;
                saveData(newData);
                if (typeof injectRows === 'function') injectRows(); // 重绘收藏列表
              }
            }
          };
          row.appendChild(delPresetBtn);

          // 原生点击逻辑"""

if s.count(old_mp_tail) != 1:
    sys.exit("❌ 预设列表锚点未唯一找到（原文件未动）")
s = s.replace(old_mp_tail, new_mp_tail, 1)
print("JS: 预设列表取消收藏按钮已注入 ✓")

# ==========================================
# 4. 原子写入与回读校验
# ==========================================
tmp_js = p_js + ".tmp"
open(tmp_js, 'w', encoding='utf-8').write(s)

final = open(tmp_js, encoding='utf-8').read()
if "Tab 长按删除预设逻辑" not in final or "tri-del-btn" not in final:
    os.remove(tmp_js)
    sys.exit(f"❌ 校验失败，已放弃写入（原文件未动，备份 {bak}）")

os.replace(tmp_js, p_js) # 原子替换
print("=== 完美！全部修改已通过校验并原子写入 ===")
