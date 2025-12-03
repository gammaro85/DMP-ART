# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Specification File for DMP-ART Standalone

Build command:
    pyinstaller DMP-ART.spec

Output:
    dist/DMP-ART/DMP-ART.exe (Windows)
    dist/DMP-ART/DMP-ART (Linux/Mac)
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Ścieżka bazowa projektu
base_path = os.path.abspath('.')

# Zbieranie wszystkich submodułów Flask i dependencies
hiddenimports = [
    'flask',
    'werkzeug',
    'jinja2',
    'click',
    'itsdangerous',
    'markupsafe',
    'PyPDF2',
    'docx',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
]

# Dodanie plików danych (templates, static, config)
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('config', 'config'),
    ('utils', 'utils'),
]

# Dodanie Flask dependencies
datas += collect_data_files('flask')
datas += collect_data_files('jinja2')

# Binaries - na razie puste (Tesseract będzie trzeba dodać manualnie lub użyć systemowego)
binaries = []

# Analysis - analiza zależności
a = Analysis(
    ['launcher.py'],
    pathex=[base_path],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tk',
        'tkinter',
        '_tkinter',
        'PyQt5',
        'PySide2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# PYZ - archiwum Pythona
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# EXE - główny executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DMP-ART',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # True = pokazuje konsole z logami (można zmienić na False dla GUI-only)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Dodać ikonę .ico jeśli będzie
)

# COLLECT - zbieranie wszystkich plików do jednego folderu
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DMP-ART'
)
