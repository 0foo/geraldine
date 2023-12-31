#!/bin/bash
pip3 uninstall geraldine 
rm ./dist/* 
poetry build 
poetry build 
pip3 cache remove geraldine 
pip3 install ./dist/geraldine-0.1.0-py3-none-any.whl
git add .
git commit -m "update"
git push
jobs -p | xargs kill -9
geri watch &
geri serve &