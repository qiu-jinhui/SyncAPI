#!/bin/bash

# 数据库迁移脚本

set -e

echo "🗄️ 开始数据库迁移..."

# 检查是否在项目目录中
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 请在项目根目录中运行此脚本"
    exit 1
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "❌ 错误: 未找到 .env 文件，请先运行 setup.sh"
    exit 1
fi

# 初始化Alembic（如果未初始化）
if [ ! -f "alembic/alembic.ini" ]; then
    echo "📝 初始化Alembic..."
    poetry run alembic init alembic
fi

# 生成迁移文件
echo "📝 生成迁移文件..."
poetry run alembic revision --autogenerate -m "Initial migration"

# 执行迁移
echo "🔄 执行数据库迁移..."
poetry run alembic upgrade head

echo "✅ 数据库迁移完成！"
