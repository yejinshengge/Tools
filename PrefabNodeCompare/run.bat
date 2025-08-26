@echo off
chcp 65001 > nul
cd /d "%~dp0"
python prefab_node_compare.py
pause 