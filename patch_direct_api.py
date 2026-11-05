import sys, shutil, re

src = 'src/rococo_v1.js'
bak = src + '.bak_direct_api'
shutil.copy(src, bak)
print('[backup]', bak)

with open(src, 'r', encoding='utf-8') as f:
    code = f.read()

if 'const chatUrl = baseURL.endsWith' in code:
    print('[skip] already patched'); sys.exit(0)

# 匹配原版 worker 请求结构（容忍多余空格和换行）
pattern = r"const workerURL = 'https://trianon-workbench\.morning-mouse-3ac4\.workers\.dev/api/chat';[\s\S]*?const nextMessages = \[\.\.\.history, \{ role: 'user', content: userText \}\];[\s\S]*?const res = await fetch\(workerURL, \{[\s\S]*?signal: myCtrl\.signal\s*\}\);"

repl = """const baseURL = config.provider.baseURL.replace(/\\/+$/, '');
      const chatUrl = baseURL.endsWith('/chat/completions') ? baseURL : baseURL + '/chat/completions';
      const nextMessages = [...history, { role: 'user', content: userText }];
      const res = await fetch(chatUrl, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer ' + config.provider.apiKey
          },
          body: JSON.stringify({
              messages: nextMessages,
              model: config.model.id,
              stream: true
          }),
          signal: myCtrl.signal
      });"""

new_code, n = re.subn(pattern, repl, code, count=1)
assert n == 1, 'regex hit=%d (check file for exact spaces/newlines)' % n
code = new_code

with open(src, 'w', encoding='utf-8') as f:
    f.write(code)

print('[ok] patched')
print('[check]', code.count('const chatUrl = baseURL.endsWith'))
