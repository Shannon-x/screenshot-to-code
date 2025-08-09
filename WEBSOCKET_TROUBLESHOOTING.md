## WebSocket连接问题解决方案

你的网站通过Cloudflare代理，这导致了WebSocket连接问题。以下是解决方案：

### 1. Cloudflare设置（推荐）
登录Cloudflare控制面板：
1. 进入你的域名设置
2. 找到 "Network" 或 "网络" 选项
3. 确保 "WebSockets" 已启用
4. 在 "SSL/TLS" 设置中，将加密模式设置为 "Full" 或 "Full (strict)"

### 2. 添加专用WebSocket子域名（备选方案）
创建一个不经过Cloudflare的子域名专门用于WebSocket：
1. 添加DNS记录：ws.code.yun7.de 直接指向你的服务器IP（灰色云朵图标）
2. 配置nginx为这个子域名提供服务
3. 修改前端代码使用新的WebSocket URL

### 3. 临时解决方案 - 使用HTTP长轮询
如果上述方案都不可行，可以考虑实现一个基于HTTP的备用通信方式。

### 当前配置状态
- 本地WebSocket连接正常工作
- Nginx配置已正确设置WebSocket代理
- 问题出在Cloudflare层面的WebSocket转发

### 测试步骤
1. 先在Cloudflare启用WebSockets
2. 清除浏览器缓存后重试
3. 如果仍有问题，查看nginx错误日志：
   ```bash
   docker exec 1Panel-openresty-CBNk tail -f /www/sites/code.yun7.de/log/error.log
   ```