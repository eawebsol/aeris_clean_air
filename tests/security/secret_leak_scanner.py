import os
import sys
import re

patterns = {
    'Gemini Key': r'AIzaSy[A-Za-z0-9_-]{33}',
    'Generic API Key': r'(?i)(api[_-]?key|secret|token|password|credential)\s*[:=]\s*[\'"][A-Za-z0-9_\-]{8,}[\'"]',
    'WAQI Token': r'(?i)waqi[_-]?token\s*[:=]\s*[\'"][a-f0-9]{30,}[\'"]',
    'Bearer Token': r'(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}'
}

scanned_files = 0
leaks = []

ignored_dirs = {'.venv', '.git', '__pycache__', '.pytest_cache', '.streamlit'}

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ignored_dirs]
    for file in files:
        if file.endswith(('.py', '.json', '.jsonl', '.md', '.toml', '.txt', '.yaml', '.yml')):
            filepath = os.path.join(root, file)
            scanned_files += 1
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        for label, pat in patterns.items():
                            if re.search(pat, line):
                                l_lower = line.lower()
                                if any(x in l_lower for x in ['your_', 'demo', 'placeholder', 'replace', 'mock', 'example', 'dummy']):
                                    continue
                                leaks.append((filepath, line_num, label, line.strip()))
            except Exception as e:
                pass

print(f"Scanned files: {scanned_files}")
print(f"Detected leaks: {len(leaks)}")
for leak in leaks:
    print(f"LEAK: {leak[0]}:{leak[1]} [{leak[2]}] -> {leak[3][:60]}...")
