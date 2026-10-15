"""检查公开源码、课程覆盖、相对链接与运行模块；只报告问题位置，不回显敏感值。"""
import ast
import json
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '.venv', '.venv-langchain', '__pycache__', '.pytest_cache'}


def public_files():
    for path in ROOT.rglob('*'):
        if path.is_file() and not EXCLUDED.intersection(path.relative_to(ROOT).parts):
            yield path


def main() -> None:
    errors = []
    links = 0
    lessons = json.loads((ROOT / 'docs/lessons.json').read_text(encoding='utf-8'))
    covered = set()
    headings = ('## 学习目标', '## 前置知识', '## 文件职责', '## 具体输入与执行过程',
                '## 运行与预期结果', '## 常见错误', '## 自测与参考答案', '<details>')
    for item in lessons:
        path = ROOT / item['path']
        if not path.is_file():
            errors.append(f'{item["id"]}: missing lesson')
            continue
        content = path.read_text(encoding='utf-8')
        for heading in headings:
            if heading not in content:
                errors.append(f'{item["path"]}: missing required section')
        if not (ROOT / item['code']).is_file():
            errors.append(f'{item["path"]}: missing code entry')
        covered.update(item['scripts'])
    for path in (ROOT / 'learning').rglob('step_*.py'):
        if path.relative_to(ROOT).as_posix() not in covered:
            errors.append(f'{path.relative_to(ROOT)}: script has no lesson')
    patterns = [
        ('private chat link', re.compile(r'thread://|codex://threads/')),
        ('absolute local path', re.compile(r'[A-Za-z]:[\\/](?:Users|codex-learnning|pythonCode)')),
        ('possible credential', re.compile(r'\bsk-[A-Za-z0-9_-]{16,}')),
        ('personal progress', re.compile(r'待答|用户说[“"]?下一步|唯一下一步|已明确授权本次')),
    ]
    for path in public_files():
        relative = path.relative_to(ROOT).as_posix()
        if path.name == '.env' or path.name.startswith('.env.') and path.name != '.env.example':
            errors.append(f'{relative}: private configuration file')
            continue
        if path.suffix not in {'.md', '.py', '.json', '.yml', '.txt', '.in', '.http'}:
            continue
        text = path.read_text(encoding='utf-8-sig')
        if path.suffix == '.py':
            try:
                ast.parse(text)
            except SyntaxError:
                errors.append(f'{relative}: invalid Python syntax')
        if path.name != 'check_docs.py':
            for label, pattern in patterns:
                for match in pattern.finditer(text):
                    line = text.count('\n', 0, match.start()) + 1
                    errors.append(f'{relative}:{line}: {label}')
        if path.suffix != '.md':
            continue
        # Exclude code fences before reading actual Markdown links.
        prose = re.sub(r'```[\s\S]*?```', '', text)
        for match in re.finditer(r'\[[^\]\n]+\]\(([^)]+)\)', prose):
            target = match[1].strip('<>')
            if re.match(r'https?://|mailto:|#', target):
                continue
            target = unquote(target.split('#', 1)[0])
            resolved = (path.parent / target).resolve()
            links += 1
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                errors.append(f'{relative}: broken or external local link')
        for match in re.finditer(r'python(?: -X utf8)? -m ([a-zA-Z_]\w*(?:\.\w+)*)', text):
            module = match[1]
            if module.split('.')[0] in {'learning','scripts','app'}:
                candidate = ROOT / module.replace('.', '/')
                if not candidate.with_suffix('.py').exists() and not (candidate/'__main__.py').exists():
                    errors.append(f'{relative}: invalid executable module {module}')
    if errors:
        print('\n'.join(sorted(set(errors))))
        raise SystemExit(1)
    print(f'DOCS_OK lessons={len(lessons)} links={links}; syntax, coverage and public-content checks passed.')


if __name__ == '__main__':
    main()
