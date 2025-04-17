# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Definir explícitamente el directorio principal
base_path = os.getcwd()  # Obtener el directorio actual de trabajo

a = Analysis(
    [os.path.join(base_path, 'main.py')],
    pathex=[base_path],
    binaries=[],
    datas=[
        (os.path.join(base_path, 'assets'), 'assets'),
        (os.path.join(base_path, 'plugins'), 'plugins'),
    ],
    hiddenimports=['project_tab', 'project_info_tab', 'project_todo_tab', 'about_tab', 'setting_tab', 'icon', 'dark_theme', 'config'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GNU Mau',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='assets/app/mau.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GNU Mau',
)

# Ajustar para empaquetar en un solo archivo
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GNU Mau',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='assets/app/mau.ico',
    onefile=True  # Esta es la configuración adicional para empaquetar en un solo archivo
)
