#!/bin/bash

# Screenshot to Code - 双层Nginx代理部署脚本
echo "🚀 开始部署 Screenshot to Code（双层代理版）..."

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

# 检查端口是否正常监听
echo "🔍 检查端口监听状态..."
if command -v netstat &> /dev/null; then
    echo "   容器nginx端口 18080:"
    netstat -tlnp | grep :18080 || echo "   ❌ 容器nginx未启动"
    echo "   容器nginx端口 18443:"
    netstat -tlnp | grep :18443 || echo "   ❌ 容器nginx未启动"
fi

# 测试容器内部服务
echo "🧪 测试容器服务..."
sleep 2
curl -s http://localhost:18080 > /dev/null && echo "✅ 容器服务正常运行" || echo "❌ 容器服务异常"

# 显示访问信息
echo ""
echo "✅ 容器部署完成！"
echo "📦 运行的容器："
echo "   - backend:  Python API"
echo "   - frontend: React应用"
echo "   - nginx:    反向代理 (端口 18080/18443)"
echo ""
echo "🌐 容器直接访问地址（测试用）："
echo "   - HTTP:  http://localhost:18080"
echo "   - HTTPS: https://localhost:18443 (如果配置了SSL)"
echo ""
echo "⚠️  下一步：配置您的主Nginx服务器"
echo "📋 请按照以下步骤配置您现有的nginx："
echo ""
echo "1️⃣  将 nginx-host.conf 的内容添加到您的nginx配置中"
echo "2️⃣  修改 server_name 为您的域名（如：copy.848999.xyz）"
echo "3️⃣  修改SSL证书路径"
echo "4️⃣  重新加载nginx配置: sudo nginx -s reload"
echo ""
echo "🔗 代理流程："
echo "   用户 → 您的nginx:443 → 容器nginx:18080 → 应用容器"
echo ""
echo "🌐 配置完成后的访问地址："
echo "   - HTTPS: https://copy.848999.xyz"
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

# 显示nginx配置提示
echo ""
echo "💡 您的主Nginx配置提示："
echo "   配置文件位置通常在:"
echo "   - Ubuntu/Debian: /etc/nginx/sites-available/"
echo "   - CentOS/RHEL:   /etc/nginx/conf.d/"
echo "   - 通用:          /etc/nginx/nginx.conf"
echo ""
echo "📄 配置示例（nginx-host.conf）："
echo "   server {"
echo "       listen 443 ssl;"
echo "       server_name copy.848999.xyz;"
echo "       # SSL配置..."
echo "       location / {"
echo "           proxy_pass http://127.0.0.1:18080;"
echo "           # 其他proxy配置..."
echo "       }"
echo "   }"

echo ""
echo "🎉 双层代理架构部署成功！"
echo "🔄 现在您的nginx只需要一个简单的proxy_pass配置即可！" 