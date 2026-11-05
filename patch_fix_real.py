#!/usr/bin/env python3

# 1. 修复 JS：把之前加的那段无用且会算错高度的代码删掉，恢复原生行为
p_js = 'src/rococo_v1.js'
s_js = open(p_js, encoding='utf-8').read()
bad_js = "\n(()=>{const _ph=field.querySelector('.ph');if(!_ph||ci.tagName!=='TEXTAREA')return;const _sync=()=>{_ph.style.height=Math.min(Math.max(ci.scrollHeight,30),120)+'px'};ci.addEventListener('input',_sync);window.addEventListener('resize',_sync);_sync()})();"

if bad_js in s_js:
    s_js = s_js.replace(bad_js, "")
    open(p_js, 'w', encoding='utf-8').write(s_js)
    print("JS 清理成功（已移除错误高度计算）。")
else:
    print("JS 警告: 未找到旧的 sync 代码。")

# 2. 修复 CSS：取消绝对定位，让输入框自然撑开外层，占位符浮动
p_css = 'src/rococo_v1.css'
s_css = open(p_css, encoding='utf-8').read()

# 精准匹配你现在的第 10 行
old_css = ".field .ph .ci{position:absolute;left:0;top:0;width:100%;height:auto;min-height:30px;max-height:120px;overflow-y:auto;resize:none;border:0;outline:0;background:none;padding:0;margin:0;"

# 改为 relative，并把 padding 设置为 4px，右侧留出 92px 防重叠
new_css = ".field .ph em,.field .ph .pht{position:absolute;left:0;top:4px;pointer-events:none}\n.field .ph .ci{position:relative;width:100%;height:auto;min-height:30px;max-height:120px;overflow-y:auto;resize:none;border:0;outline:0;background:none;padding:4px 92px 4px 0;margin:0;"

if old_css in s_css:
    s_css = s_css.replace(old_css, new_css)
    # 把第 11 行末尾多余的 padding-right:92px; 删掉（已经合并到上面的 padding 里了）
    s_css = s_css.replace("padding-right:92px;", "")
    open(p_css, 'w', encoding='utf-8').write(s_css)
    print("CSS 替换成功（绝对定位已取消）。")
else:
    print("CSS 警告: 未匹配到第 10 行的内容，请检查。")
