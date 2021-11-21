#!/bin/sh

pyinstaller --windowed --clean --onefile --distpath ./dist/linux \
    --add-data "resources/*:resources" \
    --paths ./ \
    qtpain.py