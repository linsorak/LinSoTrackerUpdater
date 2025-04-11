#!/bin/bash

source .venv/bin/activate 2>/dev/null

rm -rf dist
rm -rf __pycache__
rm -rf build

pyinstaller --clean --onefile --icon "icon.ico" "updater.py"
if [ $? -ne 0 ]; then
    echo "Erreur lors de la compilation."
    exit 1
fi

echo "Build terminé avec succès !"
