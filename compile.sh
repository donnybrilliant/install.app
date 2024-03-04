#!/bin/zsh
pyinstaller --name install --onefile --windowed --icon=icon.icns --add-data='install.sh:.' main.py
