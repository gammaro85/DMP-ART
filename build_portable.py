#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build script for a portable DMP-ART distribution without PyInstaller.

The package contains:
- application source files
- a copied local CPython runtime
- dependencies installed directly into the bundled site-packages
- one-click startup scripts for non-technical Windows users

The resulting archive avoids a custom generated .exe while keeping a
double-clickable startup flow.

Usage:
    python build_portable.py
"""

import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


DIST_DIR = Path('dist')
PACKAGE_DIR = DIST_DIR / 'DMP-ART-Portable'
RUNTIME_DIR = PACKAGE_DIR / 'runtime'
OUTPUT_ARCHIVE = DIST_DIR / 'DMP-ART-Portable.zip'

APP_FILES = [
    'app.py',
    'launcher.py',
    'requirements.txt',
    'README.md',
    'START_HERE.md',
    'BUILD.md',
    'start_portable.bat',
    'start_portable.ps1',
]

APP_DIRS = [
    'config',
    'static',
    'templates',
    'utils',
]


def print_step(message):
    print(f"\n{'=' * 72}")
    print(message)
    print('=' * 72)


def copytree_filtered(source: Path, target: Path):
    """Copy a directory tree while excluding caches and build artifacts."""
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns(
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '.git',
            '.pytest_cache',
            '.mypy_cache',
            '.ruff_cache',
        ),
        dirs_exist_ok=True,
    )


def clean_previous_build():
    print_step('Cleaning previous portable build')
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR)
    if OUTPUT_ARCHIVE.exists():
        OUTPUT_ARCHIVE.unlink()


def create_layout():
    print_step('Creating portable package layout')
    for folder in [
        PACKAGE_DIR,
        PACKAGE_DIR / 'uploads',
        PACKAGE_DIR / 'outputs',
        PACKAGE_DIR / 'outputs' / 'cache',
        PACKAGE_DIR / 'outputs' / 'dmp',
        PACKAGE_DIR / 'outputs' / 'reviews',
        RUNTIME_DIR,
    ]:
        folder.mkdir(parents=True, exist_ok=True)


def copy_application_files():
    print_step('Copying application files')
    for file_name in APP_FILES:
        source = Path(file_name)
        if not source.exists():
            raise FileNotFoundError(f'Missing required file: {source}')
        shutil.copy2(source, PACKAGE_DIR / source.name)

    for directory in APP_DIRS:
        source = Path(directory)
        if not source.exists():
            raise FileNotFoundError(f'Missing required directory: {source}')
        copytree_filtered(source, PACKAGE_DIR / source.name)


def copy_runtime_binaries():
    print_step('Copying CPython runtime')
    base_prefix = Path(sys.base_prefix)

    python_exe = base_prefix / 'python.exe'
    if not python_exe.exists():
        raise RuntimeError(
            'Portable build currently expects a Windows CPython installation '
            'with python.exe available under sys.base_prefix.'
        )

    for file_name in ['python.exe', 'pythonw.exe']:
        source = base_prefix / file_name
        if source.exists():
            shutil.copy2(source, RUNTIME_DIR / file_name)

    for pattern in ['python*.dll', 'vcruntime*.dll']:
        for source in base_prefix.glob(pattern):
            shutil.copy2(source, RUNTIME_DIR / source.name)

    for directory_name in ['DLLs', 'Lib']:
        source = base_prefix / directory_name
        if source.exists():
            copytree_filtered(source, RUNTIME_DIR / directory_name)

    (RUNTIME_DIR / 'Lib' / 'site-packages').mkdir(parents=True, exist_ok=True)


def install_required_packages():
    print_step('Installing required packages into bundled runtime')
    target_site_packages = RUNTIME_DIR / 'Lib' / 'site-packages'

    runtime_requirements = []
    for line in Path('requirements.txt').read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if stripped.lower().startswith('pyinstaller'):
            continue
        runtime_requirements.append(stripped)

    with tempfile.NamedTemporaryFile('w', suffix='-portable-requirements.txt', delete=False, encoding='utf-8') as temp_file:
        temp_file.write('\n'.join(runtime_requirements) + '\n')
        temp_requirements_path = temp_file.name

    command = [
        sys.executable,
        '-m',
        'pip',
        'install',
        '--disable-pip-version-check',
        '--no-compile',
        '--upgrade',
        '--target',
        str(target_site_packages),
        '-r',
        temp_requirements_path,
    ]
    try:
        subprocess.run(command, check=True)
    finally:
        Path(temp_requirements_path).unlink(missing_ok=True)


def write_portable_readme():
    print_step('Writing end-user startup notes')
    readme_path = PACKAGE_DIR / 'URUCHOM-NAJPIERW.txt'
    readme_path.write_text(
        'DMP-ART Portable\n'
        '=================\n\n'
        '1. Uruchom start_portable.bat\n'
        '2. Poczekaj aż przeglądarka otworzy http://localhost:5000\n'
        '3. Wszystkie dane pozostają lokalnie w folderach uploads/ i outputs/\n\n'
        'Ważne:\n'
        '- Ta paczka nie używa własnego DMP-ART.exe z PyInstallera.\n'
        '- Aplikacja uruchamia się na dołączonym runtime Pythona.\n'
        '- OCR nadal wymaga osobnej instalacji Tesseract, jeśli ma obsługiwać skany PDF.\n',
        encoding='utf-8'
    )


def verify_runtime():
    print_step('Running a focused runtime validation')
    runtime_python = RUNTIME_DIR / 'python.exe'

    compile_command = [str(runtime_python), '-s', '-m', 'py_compile', 'app.py', 'launcher.py']
    subprocess.run(compile_command, cwd=PACKAGE_DIR, check=True)

    import_command = [
        str(runtime_python),
        '-s',
        '-c',
        'import flask, PyPDF2, docx, PIL, app; print("portable runtime import ok")',
    ]
    subprocess.run(import_command, cwd=PACKAGE_DIR, check=True)


def create_archive():
    print_step('Creating portable archive')
    with zipfile.ZipFile(OUTPUT_ARCHIVE, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file_path in PACKAGE_DIR.rglob('*'):
            archive.write(file_path, file_path.relative_to(DIST_DIR))


def main():
    clean_previous_build()
    create_layout()
    copy_application_files()
    copy_runtime_binaries()
    install_required_packages()
    write_portable_readme()
    verify_runtime()
    create_archive()

    print('\nPortable package ready:')
    print(f'  {OUTPUT_ARCHIVE}')


if __name__ == '__main__':
    main()