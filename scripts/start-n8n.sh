#!/usr/bin/env zsh
# 注意: 也可以使用 #!/bin/sh 或 #!/bin/bash，都兼容

echo "🚀 启动EfficacyLens数据收集系统..."
echo ""

# 检查是否安装了Node.js和npx
if ! command -v npx &> /dev/null; then
    echo "❌ 需要先安装Node.js和npx"
    echo "请访问: https://nodejs.org/"
    echo "或者使用Homebrew: brew install node"
    exit 1
fi

echo "📦 正在启动n8n..."
echo "⏰ 首次启动可能需要1-2分钟下载依赖..."
echo ""
echo "✅ 启动完成后请访问: http://localhost:5678"
echo ""
echo "🎯 使用步骤:"
echo "1. 访问 http://localhost:5678"
echo "2. 创建账户（首次使用）"
echo "3. 点击 'Import from File'"
echo "4. 上传: workflows/n8n/one-time-trial-collector.json"
echo "5. 配置Google Sheets ID和邮箱"
echo "6. 点击 'Execute Workflow' 开始收集数据"
echo ""
echo "🛑 停止服务: 按 Ctrl+C"
echo ""

# 启动n8n
npx n8n 