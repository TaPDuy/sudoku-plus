# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


game_a = Analysis(
	['src\\game_main.py'],
	pathex=['venv\Lib\site-packages'],
	binaries=[],
	datas=[('data', 'data')],
	hiddenimports=[],
	hookspath=[],
	hooksconfig={},
	runtime_hooks=[],
	excludes=[],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=block_cipher,
	noarchive=False
)

maker_a = Analysis(['src\\maker_main.py'],
             pathex=['venv\Lib\site-packages'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

game_pyz = PYZ(game_a.pure, game_a.zipped_data, cipher=block_cipher)

game_exe = EXE(
	game_pyz,
    game_a.scripts, 
	[],
	exclude_binaries=True,
	name='Sudoku+',
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	console=True,
	disable_windowed_traceback=False,
	target_arch=None,
	codesign_identity=None,
	entitlements_file=None 
)

maker_pyz = PYZ(maker_a.pure, maker_a.zipped_data,
             cipher=block_cipher)

maker_exe = EXE(maker_pyz,
          maker_a.scripts, 
          [],
          exclude_binaries=True,
          name='Level Maker',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

coll = COLLECT(
	game_exe,
	game_a.binaries,
	game_a.zipfiles,
	game_a.datas, 
	maker_exe,
	maker_a.binaries,
	maker_a.zipfiles,
	maker_a.datas, 
	strip=False,
	upx=True,
	upx_exclude=[],
	name='sudoku_plus'
)
