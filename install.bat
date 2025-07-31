@echo off
echo ========================================
echo PRMKit 邮件迁移工具安装脚本 (UV版本)
echo ========================================
echo.

echo 检查UV环境...
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo UV未安装，正在安装UV...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo 错误: UV安装失败，请手动安装UV
        echo 访问: https://docs.astral.sh/uv/getting-started/installation/
        pause
        exit /b 1
    )
    echo UV安装成功！
else
    echo UV已安装
)

echo.
echo 检查Python环境...
uv python list
if %errorlevel% neq 0 (
    echo 安装Python 3.11...
    uv python install 3.11
)

echo.
echo 创建虚拟环境并安装依赖...
uv sync

if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步操作:
echo 1. 配置Google Cloud服务账户
echo 2. 下载服务账户JSON密钥文件
echo 3. 编辑config.json配置文件
echo 4. 运行start_server.bat启动监控面板
echo.
echo 详细说明请查看README.md文件
echo.
pause