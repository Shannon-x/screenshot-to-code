#!/bin/bash
# WebSocket测试脚本

echo "测试WebSocket连接..."

# 1. 测试本地连接
echo -e "\n1. 测试本地WebSocket连接到后端:"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" \
  -H "Upgrade: websocket" \
  -H "Connection: Upgrade" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  http://localhost:7001/generate-code || echo "直接后端连接失败"

# 2. 测试通过内部nginx
echo -e "\n2. 测试通过内部nginx (18080端口):"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" \
  -H "Upgrade: websocket" \
  -H "Connection: Upgrade" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  http://localhost:18080/generate-code || echo "内部nginx连接失败"

# 3. 检查外部nginx配置
echo -e "\n3. 检查外部nginx配置:"
docker exec 1Panel-openresty-CBNk nginx -T 2>/dev/null | grep -A20 "location /generate-code" | head -20

echo -e "\n4. 检查Cloudflare头:"
curl -s -I https://code.yun7.de | grep -i "cf-\|server"