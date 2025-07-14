#!/bin/sh
# 🌍 Safari兼容版本 - 解决Safari的安全cookie问题

printf "🚀 启动EfficacyLens数据收集系统 (Safari兼容版)...\n\n"

# 检查Node.js和npx
if ! command -v npx >/dev/null 2>&1; then
    printf "❌ 需要先安装Node.js和npx\n"
    printf "📥 安装选项:\n"
    printf "  • 官网下载: https://nodejs.org/\n"
    printf "  • macOS: brew install node\n"
    exit 1
fi

printf "📦 正在启动n8n (Safari兼容模式)...\n"
printf "🔒 已禁用安全cookie以兼容Safari\n"
printf "⏰ 首次启动可能需要1-2分钟下载依赖...\n\n"
printf "✅ 启动完成后请访问: http://localhost:5678\n\n"

printf "🎯 使用步骤:\n"
printf "1. 访问 http://localhost:5678\n"
printf "2. 创建账户（首次使用）\n"
printf "3. 点击 'Import from File'\n"
printf "4. 上传: workflows/n8n/one-time-trial-collector-simple.json\n"
printf "5. 点击 'Execute Workflow' 开始收集数据\n\n"
printf "🛑 停止服务: 按 Ctrl+C\n\n"

# 设置环境变量禁用安全cookie
export N8N_SECURE_COOKIE=false

# 启动n8n
npx n8n 