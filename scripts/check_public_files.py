"""Basic guardrail, not a full secret or vulnerability scanner."""
from pathlib import Path
import subprocess


def check():
    root=Path(__file__).resolve().parents[1]
    result=subprocess.run(['git','ls-files'],cwd=root,text=True,capture_output=True)
    names=result.stdout.splitlines() if result.returncode == 0 and (root/'.git').exists() else [str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and not any(x in p.parts for x in ['.git','__pycache__','.pytest_cache','.venv','node_modules','dist','offline-wheels'])]
    forbidden=[]
    for name in names:
        path=Path(name)
        if (path.parts and path.parts[0] in ['private_data','data']) or path.suffix in ['.sqlite3','.db','.log','.bak'] or (path.name.startswith('.env') and path.name != '.env.example') or path.name == 'MASTER_PROMPT.md':
            forbidden.append(name)
    for name in forbidden:
        print('EXCLUDE:',name)
    print('Basic private-file guard:', 'FAIL' if forbidden else 'PASS')
    return 1 if forbidden else 0

if __name__ == '__main__':
    raise SystemExit(check())

