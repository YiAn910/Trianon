import sys, shutil

src = 'src/rococo_v1.js'
bak = src + '.bak_md_hook'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

if 'window.__trianonRenderMD' in code:
    print('[skip] already patched'); sys.exit(0)

# ---- 1. 在 appendText 定义前，插入渲染钩子 + 恒等实现 ----
anchor_fn = "  const appendText = (bubble, text, scrollBox) => {"
assert code.count(anchor_fn) == 1, 'anchor_fn hit=%d' % code.count(anchor_fn)

hook = (
    "  // [MD-HOOK] Markdown 渲染钩子，先做恒等实现（不改变视觉），验证触发时机\n"
    "  if (!window.__trianonRenderMD) {\n"
    "    window.__trianonRenderMD = function(rawText) {\n"
    "      const div = document.createElement('div');\n"
    "      div.textContent = rawText;\n"
    "      return div.innerHTML.replace(/\\n/g, '<br>');\n"
    "    };\n"
    "  }\n"
    "  const renderBubbleMarkdown = (bubble, rawText) => {\n"
    "    if (!bubble || !rawText) return;\n"
    "    if (typeof window.__trianonRenderMD !== 'function') return;\n"
    "    try {\n"
    "      const html = window.__trianonRenderMD(rawText);\n"
    "      if (typeof html !== 'string' || html === '') return;\n"
    "      bubble.innerHTML = html;\n"
    "    } catch (e) { console.warn('[MD] render failed, keep plain text', e); }\n"
    "  };\n"
    "\n"
)
code = code.replace(anchor_fn, hook + anchor_fn, 1)

# ---- 2. 流式完成时渲染 ----
anchor_stream = (
    "      if (fullReply) {\n"
    "          conversationHistory = [...nextMessages, { role: 'assistant', content: fullReply }];\n"
    "          if (conversationHistory.length > 40) conversationHistory = conversationHistory.slice(-40);\n"
    "      } else if (!hasContent && statusEl.parentNode) {"
)
assert code.count(anchor_stream) == 1, 'anchor_stream hit=%d' % code.count(anchor_stream)

new_stream = (
    "      if (fullReply) {\n"
    "          renderBubbleMarkdown(myBubble, fullReply);\n"
    "          scrollToBottom(scrollBox);\n"
    "          conversationHistory = [...nextMessages, { role: 'assistant', content: fullReply }];\n"
    "          if (conversationHistory.length > 40) conversationHistory = conversationHistory.slice(-40);\n"
    "      } else if (!hasContent && statusEl.parentNode) {"
)
code = code.replace(anchor_stream, new_stream, 1)

# ---- 3. 非流式完成时渲染 ----
anchor_nonstream = (
    "              statusEl.remove();\n"
    "              appendText(myBubble, text, scrollBox);\n"
    "              conversationHistory = [...nextMessages, { role: 'assistant', content: text }];"
)
assert code.count(anchor_nonstream) == 1, 'anchor_nonstream hit=%d' % code.count(anchor_nonstream)

new_nonstream = (
    "              statusEl.remove();\n"
    "              renderBubbleMarkdown(myBubble, text);\n"
    "              scrollToBottom(scrollBox);\n"
    "              conversationHistory = [...nextMessages, { role: 'assistant', content: text }];"
)
code = code.replace(anchor_nonstream, new_nonstream, 1)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check hook def]', code.count('window.__trianonRenderMD = function'))
print('[check stream call]', code.count('renderBubbleMarkdown(myBubble, fullReply)'))
print('[check nonstream call]', code.count('renderBubbleMarkdown(myBubble, text)'))
