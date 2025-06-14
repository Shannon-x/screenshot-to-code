# 自定义AI模型配置说明

本项目现在支持使用自定义AI模型进行图片到代码的转换。您可以通过设置对话框配置自己的AI模型API。

## 功能特性

- ✅ 支持任何兼容OpenAI API格式的模型
- ✅ 支持Anthropic API格式的模型  
- ✅ 支持流式响应
- ✅ 安全的API密钥存储（仅在浏览器会话中临时存储）
- ✅ 完整的错误处理和状态反馈

## 如何配置自定义模型

1. **打开设置**: 点击界面右上角的齿轮图标
2. **启用自定义模型**: 在"自定义AI模型配置"部分，打开"启用自定义模型"开关
3. **填写模型信息**:
   - **模型名称**: 显示用的名称，如"Custom GPT-4"
   - **模型ID**: API调用时使用的模型标识符，如"gpt-4o"、"claude-3-5-sonnet"
   - **API端点URL**: 完整的API端点地址
   - **API密钥**: 访问模型服务所需的认证密钥

## 支持的API格式

### OpenAI兼容格式
```
模型ID: gpt-4o, gpt-4-turbo 等
API端点: https://api.openai.com/v1/chat/completions
或其他兼容的端点如: https://your-proxy.com/v1/chat/completions
```

### Anthropic格式  
```
模型ID: claude-3-5-sonnet, claude-3-opus 等
API端点: https://api.anthropic.com/v1/messages
```

### 其他兼容服务
大多数现代AI服务都提供OpenAI兼容的API端点，包括:
- Azure OpenAI
- 各种开源模型托管服务
- 自部署的模型服务

## 使用示例

### 示例1: 使用代理服务
- 模型名称: "Claude via Proxy"
- 模型ID: "claude-3-5-sonnet-20240620"  
- API端点: "https://your-proxy-service.com/v1/chat/completions"
- API密钥: "your-api-key"

### 示例2: 使用Azure OpenAI
- 模型名称: "Azure GPT-4"
- 模型ID: "gpt-4"
- API端点: "https://your-resource.openai.azure.com/openai/deployments/your-deployment/chat/completions?api-version=2024-02-15-preview"
- API密钥: "your-azure-key"

## 安全性说明

- API密钥只在浏览器会话期间临时存储
- 密钥不会被发送到项目服务器
- 代码生成完成后，临时存储的密钥会被自动清理
- 所有API调用都是点对点进行，不经过中间服务器

## 故障排除

### 常见问题

1. **连接失败**: 检查API端点URL是否正确，确保包含完整的协议(https://)
2. **认证错误**: 验证API密钥是否有效且具有相应权限
3. **模型不可用**: 确认模型ID在目标服务中存在且可访问
4. **响应格式错误**: 确保API端点返回标准的流式聊天响应格式

### 调试提示

- 查看浏览器开发者控制台的网络选项卡，检查API请求详情
- 检查后端日志获取详细错误信息
- 确保防火墙/代理不会阻止API调用

## 技术实现

自定义模型功能通过以下方式实现:
- 前端：添加了配置UI和参数传递
- 后端：实现了通用的HTTP客户端，支持多种API格式
- 流处理：支持实时显示生成进度
- 错误处理：提供详细的错误信息和恢复建议

## 贡献

如果您发现任何问题或有改进建议，欢迎提交Issue或Pull Request。
