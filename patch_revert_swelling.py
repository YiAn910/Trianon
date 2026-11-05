#!/usr/bin/env python3

p_css = 'src/rococo_v1.css'
s = open(p_css, encoding='utf-8').read()

# 1. 移除暴力的 height:auto!important
unlock_css = "\n/* === 解除原版高度封印，让 textarea 顺利撑开外框 === */\n.field, .field .ph { height: auto !important; }\n"
if unlock_css in s:
    s = s.replace(unlock_css, "")
    print("CSS: 已移除暴力的 height:auto!important ✓")

# 2. 移除 ci 上多余的 padding-bottom:44px
if "padding-bottom:44px}" in s:
    s = s.replace("padding-top:2px;padding-bottom:44px}", "padding-top:2px}")
    print("CSS: 已移除 .ci 多余的 padding-bottom:44px ✓")

open(p_css, 'w', encoding='utf-8').write(s)
print("=== 消肿恢复完成 ===")
