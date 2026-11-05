#!/usr/bin/env python3
import re, os, shutil, time, sys

# 1. 用你最新（包含 Markdown、弹窗、输入框）的备份作为基准，覆盖到主文件
p_src = 'src/rococo_v1.js'
p_bak = 'src/rococo_v1.js.bak_md_inline_pre'

if not os.path.exists(p_bak):
    sys.exit("❌ 找不到最新备份，请确认文件名。")

shutil.copy2(p_bak, p_src)
print("✓ 已恢复最新 Markdown + 弹窗 + 输入框版本")

s = open(p_src, encoding='utf-8').read()

# 2. 将原本走 Worker 代理的 fetch 替换为真正的 API 直连
old_fetch = """      const res = await fetch(workerURL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages: nextMessages, baseURL: config.provider.baseURL, apiKey: config.provider.apiKey, model: config.model.id }),
          signal: myCtrl.signal
      });"""

new_fetch = """      const targetURL = config.provider.baseURL.replace(/\\/+$/, '') + '/chat/completions';
      const res = await fetch(targetURL, {
          method: 'POST',
          headers: { 
              'Content-Type': 'application/json',
              'Authorization': 'Bearer ' + config.provider.apiKey
          },
          body: JSON.stringify({ messages: nextMessages, model: config.model.id }),
          signal: myCtrl.signal
      });"""

if old_fetch in s:
    s = s.replace(old_fetch, new_fetch, 1)
    print("✓ 彻底砍掉 Worker 代理，成功注入纯直连 API 逻辑")
else:
    # 兼容行号可能轻微变动的情况
    sys.exit("❌ 未找到代理代码，可能此版本已经改过直连，请检查。")

open(p_src, 'w', encoding='utf-8').write(s)
print("=== 满血复活！核心直连、Markdown、弹窗已全部就位 ===")
