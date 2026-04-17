import sys

with open("requirements.txt", "rb") as f:
    raw = f.read()

if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
    text = raw.decode("utf-16")
else:
    text = raw.decode("utf-8", errors="replace")

lines = []
for line in text.splitlines():
    line = line.strip().replace("\x00", "").replace("\r", "")
    if line and not line.startswith("#"):
        lines.append(line)

with open("req_clean.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"[fix_requirements] wrote {len(lines)} packages to req_clean.txt")
