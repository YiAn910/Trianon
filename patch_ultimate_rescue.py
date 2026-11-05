#!/usr/bin/env python3
import re, os, shutil, sys

p_src = 'src/rococo_v1.js'
p_bak = 'src/rococo_v1.js.bak_md_inline_pre'

if not os.path.exists(p_bak):
    sys.exit("❌ 找不到备份文件！")

# 1. 提取所有最新心血（弹窗、多行、删除、Markdown）
shutil.copy2(p_bak, p_src)
s = open(p_src, encoding='utf-8').read()
print("✓ 已恢复包含弹窗、多行、删除的完美最新版")

# 2. 强行修复网络请求：直连 API，并强制开启 stream: true
# 为了兼容不同的代码格式，我们用正则捕获 fetch 那段。
# 匹配 fetch(workerURL, ...) 或者 fetch(targetURL, ...)
fetch_pat = re.compile(
    r"const res = await fetch\((?:workerURL|targetURL)[^;]*?\{[\s\S]*?method:\s*'POST',[\s\S]*?headers:\s*\{[^}]+\},[\s\S]*?body:\s*JSON\.stringify\(\{[^}]+\}\),\s*signal:\s*myCtrl\.signal\s*\}\);",
    re.S
)

new_fetch = """const targetURL = config.provider.baseURL.replace(/\\/+$/, '') + '/chat/completions';
      const res = await fetch(targetURL, {
          method: 'POST',
          headers: { 
              'Content-Type': 'application/json',
              'Authorization': 'Bearer ' + config.provider.apiKey
          },
          body: JSON.stringify({ messages: nextMessages, model: config.model.id, stream: true }),
          signal: myCtrl.signal
      });"""

s, n = fetch_pat.subn(new_fetch, s, count=1)
if n == 0:
    # 如果正则没匹配到，退回精确匹配备用方案
    old_fetch = """const res = await fetch(workerURL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: nextMessages, baseURL: config.provider.baseURL, apiKey: config.provider.apiKey, model: config.model.id }),
          signal: myCtrl.signal
      });"""
    if old_fetch in s:
        s = s.replace(old_fetch, new_fetch, 1)
        print("✓ 成功将代理请求替换为纯直连，并补全 stream: true")
    else:
        sys.exit("❌ 未找到 fetch 请求代码，请截图反馈。")
else:
    print("✓ 成功将代理请求替换为纯直连，并补全 stream: true")

open(p_src, 'w', encoding='utf-8').write(s)
print("=== 满血复活完毕！请执行 python build.py ===")
