FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .

# Auto-fix UTF-16 BOM encoding that VSCode on Windows sometimes produces.
# Strips null bytes, decodes properly, writes a clean UTF-8 file, then installs.
RUN python3 -c "
with open('requirements.txt', 'rb') as f:
    raw = f.read()
# Detect UTF-16 LE or BE BOM
if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
    text = raw.decode('utf-16')
else:
    text = raw.decode('utf-8', errors='replace')
lines = []
for line in text.splitlines():
    line = line.strip().replace('\x00', '').replace('\r', '')
    if line and not line.startswith('#'):
        lines.append(line)
with open('req_clean.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
" && pip install --no-cache-dir -r req_clean.txt

# Copy rest of the app
COPY . .

CMD ["python", "main.py"]
