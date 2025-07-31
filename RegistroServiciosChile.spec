# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('data', 'data'), ('config', 'config'), ('models', 'models'), ('reports', 'reports')],
    hiddenimports=['src.domain.entities', 'src.domain.repositories', 'src.domain.validators', 'src.application.casos_uso', 'src.infrastructure.repositories', 'src.infrastructure.security', 'src.infrastructure.pdf_service', 'src.infrastructure.notification_service', 'src.infrastructure.utils', 'src.presentation.main_window', 'src.presentation.components', 'src.presentation.utils', 'src.presentation.themes', 'src.ai.prediction_service', 'src.ai.ocr_service', 'src.ai.chatbot_service'],
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
    name='RegistroServiciosChile',
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
