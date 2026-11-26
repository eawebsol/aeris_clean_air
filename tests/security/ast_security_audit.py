import ast
import os
import sys

DANGEROUS_CALLS = {'eval', 'exec', '__import__', 'compile'}
DANGEROUS_MODULES = {'pickle', 'shelve', 'subprocess', 'pty'}

issues = []

for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read(), filename=filepath)
                except Exception as e:
                    issues.append(f"Parse error in {filepath}: {e}")
                    continue

                for node in ast.walk(tree):
                    # Check dangerous calls
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id in DANGEROUS_CALLS:
                            issues.append(f"{filepath}:{node.lineno} Dangerous built-in call: {node.func.id}()")
                    # Check dangerous imports
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in DANGEROUS_MODULES:
                                issues.append(f"{filepath}:{node.lineno} Dangerous module import: {alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module in DANGEROUS_MODULES:
                            issues.append(f"{filepath}:{node.lineno} Dangerous module import: {node.module}")

print(f"AST Security Scan Complete. High-Risk Vulnerabilities Detected: {len(issues)}")
for issue in issues:
    print(f"ISSUE: {issue}")
