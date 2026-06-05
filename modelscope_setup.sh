#!/bin/bash
# ==============================================
# 魔搭（ModelScope）一键部署脚本
# ==============================================
# 在魔搭 Notebook 终端中执行：
#   bash modelscope_setup.sh
#
# 或者在终端逐行执行以下命令
# ==============================================

echo "🎵 汪苏泷 AI Agent - 魔搭部署脚本"
echo "=================================="

# Step 1: 安装依赖
echo ""
echo "📦 Step 1/3: 安装 Python 依赖..."
pip install -r requirements.txt -q

# Step 2: 设置 API Key
echo ""
echo "🔑 Step 2/3: 设置 DeepSeek API Key..."
echo "请手动设置环境变量（两种方式）："
echo ""
echo "  方式一（当前会话）："
echo "    export DEEPSEEK_API_KEY='sk-xxxxxxxxxxxxxxxx'"
echo ""
echo "  方式二（写入配置文件）："
echo '    echo "export DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx" >> ~/.bashrc'
echo "    source ~/.bashrc"
echo ""

# Step 3: 启动 Web 界面
echo ""
echo "🚀 Step 3/3: 启动 Web 界面..."
echo "运行以下命令："
echo ""
echo "    python webui.py"
echo ""
echo "=================================="
echo "启动后，魔搭会自动生成公网访问链接"
echo "在 Notebook 的输出中点击即可打开"
echo "=================================="
