@echo off
setlocal
powershell -ExecutionPolicy Bypass -File "%~dp0install_official_blender_mcp.ps1" %*
endlocal
