#!/bin/bash
pip3 uninstall geraldine 
rm ./dist/* 
poetry build 
poetry build 
pip3 cache remove geraldine 
pip3 install ./dist/geraldine-0.1.0-py3-none-any.whl --break-system-packages
