# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\claude_launch\\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['claude_launch.config', 'claude_launch.cli', 'claude_launch.ollama_api', 'claude_launch.launcher', 'rich', 'pydantic'],
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
