# rmdir /s /q "dist"
rmdir /s /q "_pycache_"
rmdir /s /q "build"

pyinstaller --clean --onefile --icon "icon.ico" "updater.py"