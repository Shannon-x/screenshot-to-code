# 截图转代码 (Screenshot to Code)

> 🚀 使用AI将截图、设计稿和Figma设计转换为干净的代码（支持HTML/Tailwind/React/Vue等）

<div align="center">
  <img src="https://github.com/abi/screenshot-to-code/assets/23818/6cebadae-2fe3-4986-ac6a-8fb9db030045" alt="演示" width="800">
</div>

## ✨ 主要特性

- 📸 **截图转代码** - 上传任何网页或应用截图，自动生成对应的前端代码
- 🎨 **支持多种框架** - HTML/CSS、Tailwind CSS、React、Bootstrap、Vue、Ionic等
- 🎯 **高精度还原** - 使用GPT-4o和Claude 3.5 Sonnet等先进模型，精确还原设计细节
- 🔄 **实时预览** - 生成代码的同时实时预览效果
- 📱 **响应式设计** - 自动生成适配各种屏幕尺寸的响应式代码
- 🎬 **视频录制克隆** - 支持录制屏幕或上传视频来克隆整个应用（实验性功能）
- 🖼️ **智能图片生成** - 使用DALL-E 3自动生成占位图片
- 🔧 **自定义模型** - 支持配置自定义的AI模型和API端点
- 💾 **Redis缓存** - 内置缓存系统，提升性能并节省API调用成本

## 🚀 快速开始

### 在线体验

访问 [https://screenshottocode.com](https://screenshottocode.com) 立即体验（付费版本）

### 本地部署

#### 前置要求

- Docker 和 Docker Compose
- Node.js 18+ (如果需要本地开发)
- Python 3.10+ (如果需要本地开发)

#### 使用Docker部署（推荐）

1. **克隆仓库**
   ```bash
   git clone https://github.com/Shannon-x/screenshot-to-code.git
   cd screenshot-to-code
   ```

2. **配置环境变量**
   ```bash
   echo "OPENAI_API_KEY=sk-your-key" > .env
   echo "ANTHROPIC_API_KEY=your-key" >> .env
   ```
   
   完整的环境变量配置：
   ```env
   # 必需 - 至少配置一个
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   
   # 可选 - 增强功能
   REPLICATE_API_KEY=your_replicate_api_key  # 用于图片生成
   
   # Redis配置（可选）
   REDIS_URL=redis://redis:6379
   
   # 自定义OpenAI代理（可选）
   OPENAI_BASE_URL=https://your-proxy.com/v1
   ```

3. **启动服务**
   ```bash
   docker-compose up -d --build
   ```

4. **访问应用**
   
   打开浏览器访问 `http://localhost:5173`

#### 本地开发环境

<details>
<summary>点击展开详细步骤</summary>

1. **后端设置**
   ```bash
   cd backend
   pip install poetry
   poetry install
   poetry shell
   poetry run uvicorn main:app --reload --port 7001
   ```

2. **前端设置**
   ```bash
   cd frontend
   yarn install
   yarn dev
   ```

3. **访问应用**
   - 前端：`http://localhost:5173`
   - 后端API：`http://localhost:7001`

</details>

## 🔧 配置说明

### API密钥配置

应用支持多种AI模型，您需要至少配置一个：

| 提供商 | 环境变量 | 说明 | 获取地址 |
|--------|----------|------|----------|
| OpenAI | `OPENAI_API_KEY` | GPT-4o模型 | [platform.openai.com](https://platform.openai.com) |
| Anthropic | `ANTHROPIC_API_KEY` | Claude 3.5 Sonnet | [console.anthropic.com](https://console.anthropic.com) |
| Google | `GEMINI_API_KEY` | Gemini模型 | [makersuite.google.com](https://makersuite.google.com) |
| Replicate | `REPLICATE_API_KEY` | 图片生成模型 | [replicate.com](https://replicate.com) |

### Redis缓存配置

Redis用于缓存生成结果，提升性能并减少API调用：

```yaml
# docker-compose.yml 已包含Redis服务
redis:
  image: redis:7-alpine
  restart: unless-stopped
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data
  command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

Redis配置说明：
- `appendonly yes` - 启用持久化，防止数据丢失
- `maxmemory 256mb` - 限制最大内存使用
- `maxmemory-policy allkeys-lru` - 内存满时使用LRU算法淘汰键

📚 **[查看详细的Redis部署指南](docs/redis-deployment-guide.md)** - 包含性能优化、监控维护、故障排除等内容

### 自定义模型配置

支持配置兼容OpenAI API的自定义模型：

1. 在设置对话框中启用"使用自定义模型"
2. 配置以下参数：
   - 模型ID（如：gpt-4-vision-preview）
   - 服务URL（如：https://api.example.com/v1）
   - API密钥

### 代理配置

如果您无法直接访问OpenAI API（如地区限制），可以配置代理：

1. **环境变量方式**
   ```bash
   OPENAI_BASE_URL=https://your-proxy.com/v1
   ```

2. **界面配置方式**
   在设置对话框中配置OpenAI基础URL

注意：URL必须包含"v1"路径

## 📚 使用指南

### 基本使用流程

1. **上传截图**
   - 拖拽图片到上传区域
   - 或使用 Ctrl/Cmd + V 粘贴
   - 支持 PNG、JPG、JPEG 格式
   - 最大文件大小：20MB

2. **选择输出格式**
   - HTML + Tailwind CSS（推荐）
   - HTML + 纯CSS
   - React + Tailwind
   - Bootstrap
   - Vue + Tailwind
   - Ionic + Tailwind
   - SVG

3. **生成代码**
   - 点击"生成"按钮
   - 等待AI处理（通常需要10-30秒）
   - 实时查看生成进度

4. **预览��导出**
   - 在右侧实时预览生成的页面
   - 切换桌面/平板/手机视图
   - 复制代码或下载文件

### 高级功能

#### 视频克隆功能

1. 点击"录制屏幕"或上传视频文件（支持.mp4、.mov、.webm）
2. 系统会分析视频中的界面变化
3. 生成完整的交互式应用代码

[了解更多视频功能](https://github.com/abi/screenshot-to-code/wiki/Screen-Recording-to-Code)

#### 更新现有代码

1. 导入您的现有代码
2. 上传新的设计稿
3. AI会智能更新代码而不是重写

#### 批量处理

支持同时生成多个变体，对比选择最佳结果

### 调试模式

如果不想消耗API额度进行调试，可以使用mock模式：

```bash
MOCK=true poetry run uvicorn main:app --reload --port 7001
```

## 🛠️ 技术架构

### 后端技术栈

- **FastAPI** - 高性能Python Web框架
- **WebSocket** - 实时通信
- **Redis** - 缓存和消息队列
- **Poetry** - 依赖管理
- **异步处理** - 提升并发性能

### 前端技术栈

- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式框架
- **Vite** - 构建工具
- **Zustand** - 状态管理

### AI模型集成

- **OpenAI GPT-4o** - 主要代码生成模型
- **Claude 3.5 Sonnet** - 高质量代码生成
- **Gemini** - Google的多模态模型
- **DALL-E 3** - 图片生成
- **Flux Schnell** - 通过Replicate的图片生成

## 🔒 安全性

- API密钥仅存储在您的浏览器本地，不会上传到服务器
- 支持自托管部署，完全控制您的数据
- WebSocket连接支持SSL/TLS加密
- 内置请求频率限制和异常处理

## 🤔 常见问题

**Q: 如何获取OpenAI API密钥？**
A: 访问 [platform.openai.com](https://platform.openai.com) 注册并创建API密钥。确保您的账户有GPT-4权限。

**Q: 后端启动报错怎么办？**
A: 请查看 [故障排除指南](https://github.com/abi/screenshot-to-code/blob/main/Troubleshooting.md)

**Q: Windows上出现UTF-8错误？**
A: 使用Notepad++打开.env文件，选择编码->UTF-8

**Q: 如何配置前端连接到不同的后端地址？**
A: 在 `frontend/.env.local` 中配置：
```
VITE_HTTP_BACKEND_URL=http://your-backend:7001
VITE_WS_BACKEND_URL=ws://your-backend:7001
```

**Q: 支持哪些图片格式？**
A: 支持PNG、JPG、JPEG格式，最大20MB

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 如何贡献

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 开发规范

- 遵循现有的代码风格
- 添加适当的测试
- 更新相关文档
- 提交信息要清晰明了

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 感谢 OpenAI、Anthropic 和 Google 提供强大的AI模型
- 感谢所有贡献者和用户的支持
- 特别感谢 [原始项目](https://github.com/abi/screenshot-to-code) 的作者 [@abi](https://twitter.com/_abi_)

## 📞 联系方式

- 问题反馈：[GitHub Issues](https://github.com/Shannon-x/screenshot-to-code/issues)
- 功能建议：[GitHub Discussions](https://github.com/Shannon-x/screenshot-to-code/discussions)
- Twitter: [@_abi_](https://twitter.com/_abi_)

## 📸 更多示例

查看 [示例页面](https://github.com/abi/screenshot-to-code/wiki/Examples) 了解更多使用案例

---

<div align="center">
  <p>如果这个项目对您有帮助，请给我们一个 ⭐️</p>
  <p>Made with ❤️ by the Screenshot to Code team</p>
</div>