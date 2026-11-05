import sys, shutil

src = 'src/rococo_v1.js'
bak = src + '.bak_markdown_real'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

if 'window.markdownit' in code:
    print('[skip] already patched'); sys.exit(0)

# 1. 替换恒等钩子为真正的 Markdown 渲染
old_hook = """  if (!window.__trianonRenderMD) {
    window.__trianonRenderMD = function(rawText) {
      const div = document.createElement('div');
      div.textContent = rawText;
      return div.innerHTML.replace(/\\n/g, '<br>');
    };
  }"""
assert code.count(old_hook) == 1, 'old_hook hit=%d' % code.count(old_hook)

new_hook = """  if (!window.__trianonRenderMD) {
    window.__trianonRenderMD = function(rawText) {
      if (window.markdownit && window.hljs) {
        const md = window.markdownit({
          html: false,
          linkify: true,
          highlight: function (str, lang) {
            if (lang && window.hljs.getLanguage(lang)) {
              try {
                return '<pre class="hljs"><code>' +
                       window.hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
                       '</code></pre>';
              } catch (__) {}
            }
            return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
          }
        });
        return md.render(rawText);
      }
      const div = document.createElement('div');
      div.textContent = rawText;
      return div.innerHTML.replace(/\\n/g, '<br>');
    };
  }"""
code = code.replace(old_hook, new_hook, 1)

# 2. 在 window.__real 挂载处，加入 CDN 注入和样式
anchor_real = "window.__real = { chat, destroy };"
assert code.count(anchor_real) == 1, 'anchor_real hit=%d' % code.count(anchor_real)

cdn_inject = anchor_real + """
  // [CDN-MD] 动态注入 Markdown 解析器、代码高亮库及样式
  (function injectMarkdownCDN() {
    if (!document.getElementById('hljs-css')) {
      const link = document.createElement('link');
      link.id = 'hljs-css';
      link.rel = 'stylesheet';
      link.href = 'https://cdn.bootcdn.net/ajax/libs/highlight.js/11.9.0/styles/github.min.css';
      document.head.appendChild(link);
    }
    if (!document.getElementById('hljs-js')) {
      const s1 = document.createElement('script');
      s1.id = 'hljs-js';
      s1.src = 'https://cdn.bootcdn.net/ajax/libs/highlight.js/11.9.0/highlight.min.js';
      document.head.appendChild(s1);
    }
    if (!document.getElementById('mdit-js')) {
      const s2 = document.createElement('script');
      s2.id = 'mdit-js';
      s2.src = 'https://cdn.bootcdn.net/ajax/libs/markdown-it/14.1.0/markdown-it.min.js';
      document.head.appendChild(s2);
    }
    if (!document.getElementById('md-style')) {
      const style = document.createElement('style');
      style.id = 'md-style';
      style.textContent = `
        .real-bubble.a p { margin: 0 0 8px 0; }
        .real-bubble.a p:last-child { margin-bottom: 0; }
        .real-bubble.a pre { background: #F4F6F9; padding: 12px; border-radius: 6px; overflow-x: auto; border: 1px solid #E1E6F0; margin: 10px 0; }
        .real-bubble.a code { font-family: Consolas, Monaco, monospace; font-size: 13.5px; background: #F4F6F9; padding: 2px 4px; border-radius: 4px; color: #D14; }
        .real-bubble.a pre code { background: transparent; padding: 0; color: inherit; }
        .real-bubble.a ul, .real-bubble.a ol { margin: 8px 0; padding-left: 20px; }
        .real-bubble.a blockquote { border-left: 3px solid #C5D0E5; margin: 8px 0; padding-left: 10px; color: #666; }
      `;
      document.head.appendChild(style);
    }
  })();
"""
code = code.replace(anchor_real, cdn_inject, 1)

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check hook]', code.count('window.markdownit'))
print('[check cdn]', code.count('injectMarkdownCDN'))
