#!/usr/bin/env python3
import re, os, shutil, time, sys

p_js = 'src/rococo_v1.js'
if not os.path.exists(p_js):
    sys.exit(f"❌ 找不到 {p_js}")
shutil.copy2(p_js, f"{p_js}.bak_delete.{int(time.time())}")
s = open(p_js, encoding='utf-8').read()

# 1. 管理页：在 actionDiv 中注入删除按钮
# 找到 actionDiv 生成完毕之后、追加到 row 之前的位置。我们匹配 `if (isActive || m.starred) {` 后面的收尾代码
old_mdl_tail = """              if (isActive || m.starred) {
                actionDiv.appendChild(starBtn);
              }
            }"""
# 使用精确替换，在其后加入删除逻辑
new_mdl_tail = """              if (isActive || m.starred) {
                actionDiv.appendChild(starBtn);
              }
              
              // === 注入洛可可风删除按钮（管理页） ===
              const delBtn = document.createElement('div');
              delBtn.style.cssText = 'cursor: pointer; display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; opacity: 0.3; transition: all 0.2s;';
              delBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="#7C8DB5" stroke-width="1.2" stroke-linecap="round"><path d="M2,2 L10,10 M10,2 L2,10"/></svg>';
              delBtn.onmouseenter = () => { delBtn.style.opacity = '1'; delBtn.style.transform = 'scale(1.15) rotate(90deg)'; delBtn.querySelector('svg').setAttribute('stroke', '#A65B68'); };
              delBtn.onmouseleave = () => { delBtn.style.opacity = '0.3'; delBtn.style.transform = 'none'; delBtn.querySelector('svg').setAttribute('stroke', '#7C8DB5'); };
              
              delBtn.onclick = (ev) => {
                ev.stopPropagation(); // 阻止选中模型
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

if new_mdl_tail not in s:
    if old_mdl_tail in s:
        s = s.replace(old_mdl_tail, new_mdl_tail)
        print("JS: 管理页模型删除按钮注入成功 ✓")
    else:
        sys.exit("❌ 未找到管理页 actionDiv 的结尾锚点。")

# 2. 预设列表：在 row 中注入取消收藏按钮
old_mp_tail = """          ckSvg.appendChild(ckPath);
          row.appendChild(ckSvg);

          // 原生点击逻辑"""

new_mp_tail = """          ckSvg.appendChild(ckPath);
          row.appendChild(ckSvg);

          // === 注入洛可可风删除按钮（预设页） ===
          const delPresetBtn = document.createElement('div');
          delPresetBtn.style.cssText = 'margin-left: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; width: 16px; height: 16px; opacity: 0.3; transition: all 0.2s;';
          delPresetBtn.innerHTML = '<svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="#7C8DB5" stroke-width="1.2" stroke-linecap="round"><path d="M2,2 L10,10 M10,2 L2,10"/></svg>';
          delPresetBtn.onmouseenter = () => { delPresetBtn.style.opacity = '1'; delPresetBtn.style.transform = 'rotate(90deg)'; delPresetBtn.querySelector('svg').setAttribute('stroke', '#A65B68'); };
          delPresetBtn.onmouseleave = () => { delPresetBtn.style.opacity = '0.3'; delPresetBtn.style.transform = 'none'; delPresetBtn.querySelector('svg').setAttribute('stroke', '#7C8DB5'); };
          
          delPresetBtn.onclick = (ev) => {
            ev.stopPropagation(); // 阻止选中模型
            const newData = getData();
            const pr = newData.providers.find(x => x.id === p.id);
            if (pr) {
              const mm = pr.models.find(x => x.id === m.id);
              if (mm) {
                mm.starred = false;
                saveData(newData);
                if (typeof injectRows === 'function') injectRows(); // 重新渲染预设列表
              }
            }
          };
          row.appendChild(delPresetBtn);

          // 原生点击逻辑"""

if new_mp_tail not in s:
    if old_mp_tail in s:
        s = s.replace(old_mp_tail, new_mp_tail)
        print("JS: 预设列表取消收藏按钮注入成功 ✓")
    else:
        sys.exit("❌ 未找到预设页 ckSvg 的结尾锚点。")

open(p_js, 'w', encoding='utf-8').write(s)

# 严格回读校验
final = open(p_js, encoding='utf-8').read()
if "注入洛可可风删除按钮（管理页）" not in final or "注入洛可可风删除按钮（预设页）" not in final:
    sys.exit("❌ 校验失败：注入未生效！")

print("=== 完美！删除功能已全部注入（备有备份，出问题可随时还原） ===")
