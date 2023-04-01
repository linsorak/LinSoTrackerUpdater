call activate LinSoTracker

# rmdir /s /q "dist"
rmdir /s /q "_pycache_"
rmdir /s /q "build"

pyinstaller --clean --onefile --icon "icon.ico" "updater.py"

call conda deactivate