import sys, shutil

src = 'src/rococo_v1.js'
bak = src + '.bak_ck_and_on'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

# 防重复执行
if "ckSvg.setAttribute('class', 'ck')" in code:
    print('[skip] already patched, exit')
    sys.exit(0)

# ---- 补丁1：在 row.appendChild(b); 后插入原版对勾 svg.ck ----
anchor1 = "          b.textContent = m.name;\n          row.appendChild(b);\n"
assert code.count(anchor1) == 1, 'anchor1 hit=%d' % code.count(anchor1)

insert1 = anchor1 + (
    "          // 原版对勾 SVG（与真实 .mp-row 结构一致）\n"
    "          const ckSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');\n"
    "          ckSvg.setAttribute('class', 'ck');\n"
    "          ckSvg.setAttribute('width', '15');\n"
    "          ckSvg.setAttribute('height', '13');\n"
    "          ckSvg.setAttribute('viewBox', '0 0 15 13');\n"
    "          ckSvg.setAttribute('aria-hidden', 'true');\n"
    "          const ckPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');\n"
    "          ckPath.setAttribute('d', 'M1.8,7.2 C3.3,8.4 4.6,9.8 5.7,11.3 C7.9,7.2 10.6,3.9 13.4,1.6');\n"
    "          ckPath.setAttribute('fill', 'none');\n"
    "          ckPath.setAttribute('stroke', '#4A5A86');\n"
    "          ckPath.setAttribute('stroke-width', '1.55');\n"
    "          ckPath.setAttribute('stroke-linecap', 'round');\n"
    "          ckPath.setAttribute('stroke-linejoin', 'round');\n"
    "          ckSvg.appendChild(ckPath);\n"
    "          row.appendChild(ckSvg);\n"
)
code = code.replace(anchor1, insert1, 1)

# ---- 补丁2：点击时立即同步 on 类 ----
anchor2 = (
    "          row.onclick = () => {\n"
    "            const newData = getData();\n"
    "            newData.activeModel = { providerId: p.id, modelId: m.id };\n"
    "            saveData(newData);\n"
)
assert code.count(anchor2) == 1, 'anchor2 hit=%d' % code.count(anchor2)

insert2 = (
    "          row.onclick = (ev) => {\n"
    "            if (ev) ev.stopPropagation();\n"
    "            // 立即同步高亮（不等下次打开）\n"
    "            const mvEl = document.getElementById('mpMv');\n"
    "            if (mvEl) {\n"
    "              mvEl.querySelectorAll('.mp-row').forEach(r => {\n"
    "                r.classList.remove('on');\n"
    "                r.setAttribute('aria-checked', 'false');\n"
    "              });\n"
    "            }\n"
    "            row.classList.add('on');\n"
    "            row.setAttribute('aria-checked', 'true');\n"
    "\n"
    "            const newData = getData();\n"
    "            newData.activeModel = { providerId: p.id, modelId: m.id };\n"
    "            saveData(newData);\n"
)
code = code.replace(anchor2, insert2, 1)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check svg.ck]', code.count("ckSvg.setAttribute('class', 'ck')"))
print('[check immediate on]', code.count('// 立即同步高亮'))
