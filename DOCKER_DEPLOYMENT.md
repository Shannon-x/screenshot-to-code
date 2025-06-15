# 🐳 Screenshot to Code - 容器化部署指南

## 📖 概述

这个解决方案通过Docker容器化彻底解决了WebSocket混合内容问题，使用以下架构：

```
[浏览器] → [Nginx反向代理] → [前端容器]
                    ↓
              [后端容器]
```

## 🔧 架构特点

### ✅ **解决的问题**
- ✅ WebSocket混合内容错误 (Mixed Content)
- ✅ CORS跨域问题
- ✅ SSL/TLS证书配置复杂性
- ✅ 容器间网络通信
- ✅ 开发和生产环境一致性

### 🏗️ **架构组件**
1. **Nginx反向代理** - 处理所有HTTP/HTTPS请求和WebSocket升级
2. **前端容器** - React应用（Vite开发服务器）
3. **后端容器** - Python FastAPI WebSocket服务器
4. **Docker网络** - 内部容器通信

## 🚀 快速部署

### 方法1: 使用部署脚本（推荐）

```bash
# 1. 运行部署脚本
./deploy.sh

# 2. 按提示编辑.env文件，添加API密钥
nano .env

# 3. 重新运行部署
./deploy.sh
```

### 方法2: 手动部署

```bash
# 1. 创建环境变量文件
cp .env.example .env
nano .env  # 添加您的API密钥

# 2. 启动服务
docker-compose up --build -d

# 3. 查看状态
docker-compose ps
```

## 📂 配置文件说明

### `docker-compose.yml`
- 定义了三个服务：backend、frontend、nginx
- 配置了内部网络通信
- 设置了环境变量和端口映射

### `nginx.conf`
- 反向代理配置
- WebSocket升级处理
- SSL/HTTPS支持（可选）

### `frontend/src/config.ts`
- 智能协议选择
- 容器环境检测
- 同源策略处理

## 🌐 访问地址

部署完成后，您可以通过以下地址访问：

- **HTTP**: http://localhost
- **HTTPS**: https://localhost（如果配置了SSL）
- **开发端口**: http://localhost:5173（直接访问前端）

## 🔍 监控和调试

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f nginx
```

### 检查容器状态
```bash
# 查看容器状态
docker-compose ps

# 进入容器调试
docker-compose exec frontend sh
docker-compose exec backend sh
```

### 测试WebSocket连接
```bash
# 测试后端健康状态
curl http://localhost/api/health

# 检查WebSocket端点
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  http://localhost/generate-code
```

## 🛠️ 自定义配置

### 修改端口
在 `docker-compose.yml` 中修改端口映射：
```yaml
nginx:
  ports:
    - "8080:80"  # 修改为8080端口
    - "8443:443"
```

### 添加SSL证书
1. 将证书文件放在 `ssl/` 目录中
2. 取消 `nginx.conf` 中HTTPS配置的注释
3. 修改 `docker-compose.yml` 挂载SSL目录

### 环境变量
在 `.env` 文件中配置：
```bash
# API密钥
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-key-here

# 后端配置
BACKEND_PORT=7001
IS_PROD=true

# 前端配置（Docker自动设置）
VITE_WS_BACKEND_URL=ws://backend:7001
VITE_HTTP_BACKEND_URL=http://backend:7001
```

## 🐛 常见问题

### Q: WebSocket连接仍然失败
**A**: 检查以下内容：
1. 确保所有容器都在运行：`docker-compose ps`
2. 检查Nginx配置是否正确
3. 查看Nginx日志：`docker-compose logs nginx`

### Q: 无法访问localhost
**A**: 检查端口是否被占用：
```bash
netstat -tlnp | grep :80
netstat -tlnp | grep :443
```

### Q: API调用失败
**A**: 确保在 `.env` 文件中设置了正确的API密钥

### Q: 前端热重载不工作
**A**: 这是正常的，因为通过Nginx代理。开发时可以直接访问 `http://localhost:5173`

## 📋 生产环境部署

### 域名配置
1. 修改 `nginx.conf` 中的 `server_name`
2. 配置DNS解析到您的服务器
3. 获取SSL证书（Let's Encrypt推荐）

### 性能优化
```yaml
# docker-compose.prod.yml
services:
  frontend:
    build:
      target: production  # 使用生产构建
    
  nginx:
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf:ro
```

### 安全配置
- 限制API访问
- 配置防火墙规则
- 使用环境变量管理密钥
- 定期更新容器镜像

## 🎯 总结

这个容器化解决方案提供了：

1. **完全解决WebSocket混合内容问题**
2. **统一的开发和生产环境**
3. **简化的部署流程**
4. **内置的SSL/TLS支持**
5. **水平扩展能力**

通过使用Docker网络和Nginx反向代理，我们实现了真正的"同源"WebSocket连接，彻底解决了浏览器安全限制带来的问题。

---

**需要帮助？** 请查看日志文件或创建GitHub Issue。 