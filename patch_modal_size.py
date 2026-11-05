#!/usr/bin/env python3
import os, sys, re
p_js = 'src/rococo_v1.js'
s = open(p_js, encoding='utf-8').read()
s = s.replace("max-width: 380px;", "max-width: 320px;")
s = s.replace("padding: 28px 32px;", "padding: 20px 24px;")
s = s.replace("margin-bottom: 24px;", "margin-bottom: 16px;")
open(p_js, 'w', encoding='utf-8').write(s)
print("✓ 弹窗尺寸已收紧（更精致小巧）")
