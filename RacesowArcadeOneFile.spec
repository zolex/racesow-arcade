# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['RacesowArcade.pyw'],
    pathex=[],
    binaries=[],
    datas=[
        ('./README.md', '.'),
        ('./assets', './assets')
    ],
    hiddenimports=[],
    hooksconfig={},
    runtime_hooks=['./hooks/set_env.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)


splash = Splash('./assets/graphics/splash.jpg',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=(10, 30),
                text_size=10,
                text_color='white',
                always_on_top=True)

exe = EXE(
    pyz,
    splash,
    splash.binaries,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RacesowArcade',
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
)
