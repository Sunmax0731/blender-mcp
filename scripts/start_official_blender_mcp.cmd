@echo off
setlocal
powershell -ExecutionPolicy Bypass -File "%~dp0start_official_blender_mcp.ps1" %*
endlocal
