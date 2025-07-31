@echo off
echo 启动PRMKit邮件迁移监控面板 (UV版本)...
echo.
echo 请确保已运行安装脚本:
echo install.bat
echo.
echo 访问地址: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo.
uv run python app.py
pause