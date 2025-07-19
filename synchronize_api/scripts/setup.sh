#!/bin/bash

# 同步API项目环境设置脚本

set -e

echo "🚀 开始设置同步API项目环境..."

# 检查Python版本
echo "📋 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 错误: 需要Python $required_version或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python版本检查通过: $python_version"

# 检查Poetry是否安装
if ! command -v poetry &> /dev/null; then
    echo "📦 安装Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "✅ Poetry已安装"
fi

# 安装依赖
echo "📦 安装项目依赖..."
poetry install

# 创建环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp env.example .env
    echo "✅ 环境变量文件已创建，请编辑 .env 文件配置数据库连接等信息"
else
    echo "✅ 环境变量文件已存在"
fi

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 检查Docker是否安装
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Docker已安装，可以运行以下命令启动开发环境:"
    echo "   docker-compose up -d"
else
    echo "⚠️  Docker未安装，请手动安装Docker和Docker Compose"
fi

echo ""
echo "🎉 环境设置完成！"
echo ""
echo "📋 下一步操作:"
echo "1. 编辑 .env 文件配置数据库连接等信息"
echo "2. 运行数据库迁移: poetry run alembic upgrade head"
echo "3. 启动应用: poetry run uvicorn src.main:app --reload"
echo "4. 或者使用Docker: docker-compose up -d"
echo ""
echo "📚 更多信息请查看 README.md 文件"
