# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Boot.py'],
    pathex=[],
    binaries=[],
    datas=[('config.yml', '.'), ('creds.yml', '.'), ('test_net_creds.yml', '.'), ('megatronmod_strategy.py', '.')],
    hiddenimports=['talib.stream'],
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
    name='Boot',
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
