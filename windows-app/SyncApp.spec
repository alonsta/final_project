# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SyncApp.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['httpx', 'win32event', 'keyring.backends.Windows', 'watchdog', 'watchdog.events', 'watchdog.observers', 'tkinter', 'winerror', 'win32api', 'win32event', 'socket', 'pyuac', 'httpx'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SyncApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app.ico'],
)
