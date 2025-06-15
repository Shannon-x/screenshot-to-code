#!/bin/bash

# Screenshot to Code - 容器化部署脚本
echo "🚀 开始部署 Screenshot to Code..."

# 检查必要的文件
if [ ! -f ".env" ]; then
    echo "⚠️  创建 .env 文件..."
    cat > .env << EOL
# OpenAI API Key (必需)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (可选)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 后端端口
BACKEND_PORT=7001

# 生产环境标志
IS_PROD=true
EOL
    echo "✅ 已创建 .env 文件，请编辑并添加您的API密钥"
    echo "📝 编辑命令: nano .env 或 vim .env"
    exit 1
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down

# 清理旧镜像（可选）
echo "🧹 清理旧镜像..."
docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || true

# 构建并启动容器
echo "🔨 构建并启动容器..."
docker-compose up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "✅ 部署完成！"
echo "🌐 访问地址："
echo "   - HTTP:  http://localhost"
echo "   - HTTPS: https://localhost (如果配置了SSL)"
echo ""
echo "📝 查看日志命令："
echo "   - 所有服务: docker-compose logs -f"
echo "   - 前端:    docker-compose logs -f frontend"
echo "   - 后端:    docker-compose logs -f backend"
echo "   - Nginx:   docker-compose logs -f nginx"
echo ""
echo "🔧 管理命令："
echo "   - 停止:    docker-compose down"
echo "   - 重启:    docker-compose restart"
echo "   - 重建:    docker-compose up --build -d"

# 检查端口占用
if command -v netstat &> /dev/null; then
    echo ""
    echo "🔍 端口占用情况："
    netstat -tlnp | grep -E ":(80|443|5173|7001)\s" 2>/dev/null || echo "   无相关端口占用"
fi

echo ""
echo "🎉 Screenshot to Code 已成功部署！" 