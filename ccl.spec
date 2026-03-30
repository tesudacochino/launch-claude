# -*- mode: python ; coding: utf-8 -*-

import os
import glob

# Generar archivo con el commit hash ANTES de hacer el glob
commit_hash = os.environ.get('CCL_COMMIT_HASH', '')
if commit_hash:
    with open('src/claude_launch/_commit.py', 'w') as f:
        f.write(f'COMMIT_HASH = "{commit_hash}"\n')
    print(f"Generated _commit.py with hash: {commit_hash}")
else:
    # Asegurarse de que el archivo existe incluso si está vacío
    with open('src/claude_launch/_commit.py', 'w') as f:
        f.write('COMMIT_HASH = ""\n')
    print("No CCL_COMMIT_HASH found, generated empty _commit.py")

# Incluir todo el paquete claude_launch
datas = []
# Incluir todos los .py files del paquete (incluyendo _commit.py recién generado)
for py_file in glob.glob('src/claude_launch/*.py'):
    datas.append((py_file, 'claude_launch'))
    print(f"Adding to datas: {py_file}")

# Incluir pyproject.toml para obtener version si __version__ falla
datas.append(('pyproject.toml', '.'))

a = Analysis(
    ['src/claude_launch/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['claude_launch.config', 'claude_launch.cli', 'claude_launch.ollama_api', 'claude_launch.launcher', 'claude_launch._commit', 'rich', 'pydantic'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ccl',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
