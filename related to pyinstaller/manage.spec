# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['store_application_full\\manage.py'],
             pathex=['C:\\Users\\khale\\OneDrive\\Desktop\\applactionExe_3'],
             binaries=[],
            datas=[('C:\\Users\\khale\\OneDrive\\Desktop\\applactionExe_3\\store_application_full\\content\\templates\\content','templates\\content'),
					('C:\\Users\\khale\\OneDrive\\Desktop\\applactionExe_3\\store_application_full\\content\\static\\content','static\\content')],
             hiddenimports=['content.urls'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='application',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='application')
