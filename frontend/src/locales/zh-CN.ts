// 中文本地化文件
export const zhCN = {
  // 通用
  common: {
    cancel: "取消",
    confirm: "确认",
    save: "保存",
    delete: "删除",
    close: "关闭",
    error: "错误",
    success: "成功",
    warning: "警告",
    loading: "加载中...",
    generating: "生成中...",
    uploading: "上传中...",
    downloading: "下载中...",
    copied: "已复制",
    copyToClipboard: "复制到剪贴板",
    paste: "粘贴",
    clear: "清除",
    reset: "重置",
    back: "返回",
    next: "下一步",
    finish: "完成",
    yes: "是",
    no: "否",
  },

  // 应用状态
  appState: {
    initial: "初始状态",
    codingInProgress: "代码生成中",
    coding: "编码中",
    updating: "更新中",
  },

  // 输入模式
  inputMode: {
    image: "图片模式",
    video: "视频模式", 
    text: "文本模式",
  },

  // 主界面
  main: {
    title: "截图转代码",
    description: "将截图转换为干净的代码（HTML/Tailwind/React）",
    startTitle: "开始使用",
    uploadScreenshot: "上传截图",
    dragDropHint: "拖拽图片到此处或点击上传",
    pasteHint: "或者粘贴图片 (Ctrl/Cmd + V)",
    generateFromText: "从文本生成",
    textPromptPlaceholder: "描述您想要创建的界面...",
    importCode: "导入代码",
    importCodePlaceholder: "粘贴您现有的代码...",
    takeScreenshot: "截取屏幕",
    recordVideo: "录制视频",
    stopRecording: "停止录制",
    createNew: "创建新项目",
    updateCode: "更新代码",
    regenerate: "重新生成",
    viewHistory: "查看历史",
    downloadCode: "下载代码",
    shareProject: "分享项目",
  },

  // 设置对话框
  settings: {
    title: "设置",
    generalTab: "常规",
    apiKeysTab: "API密钥",
    advancedTab: "高级",
    
    // API密钥
    openAiApiKey: "OpenAI API密钥",
    openAiApiKeyPlaceholder: "sk-...",
    openAiBaseUrl: "OpenAI基础URL（可选）",
    openAiBaseUrlPlaceholder: "https://api.openai.com/v1",
    anthropicApiKey: "Anthropic API密钥",
    anthropicApiKeyPlaceholder: "sk-ant-...",
    screenshotOneApiKey: "ScreenshotOne API密钥",
    customModelSettings: "自定义模型设置",
    useCustomModel: "使用自定义模型",
    customModelId: "模型ID",
    customModelIdPlaceholder: "例如：gpt-4-vision-preview",
    customModelServiceUrl: "服务URL",
    customModelServiceUrlPlaceholder: "https://api.example.com/v1/chat/completions",
    customModelApiKey: "API密钥",
    
    // 代码生成设置
    codeGenerationModel: "代码生成模型",
    outputFormat: "输出格式",
    enableImageGeneration: "启用图片生成",
    editorTheme: "编辑器主题",
    
    // 主题选项
    themes: {
      cobalt: "Cobalt",
      oneDark: "One Dark",
      githubDark: "GitHub Dark",
      githubLight: "GitHub Light",
      monokai: "Monokai",
      terminal: "Terminal",
    },
    
    // 输出格式选项
    stacks: {
      htmlTailwind: "HTML + Tailwind",
      htmlCss: "HTML + CSS", 
      reactTailwind: "React + Tailwind",
      bootstrap: "Bootstrap",
      ionicTailwind: "Ionic + Tailwind",
      vueTailwind: "Vue + Tailwind",
      svg: "SVG",
    },
    
    saveSuccess: "设置已保存",
    saveError: "保存设置失败",
  },

  // 预览面板
  preview: {
    title: "预览",
    desktop: "桌面视图",
    tablet: "平板视图",
    mobile: "手机视图",
    fullscreen: "全屏",
    exitFullscreen: "退出全屏",
    refresh: "刷新",
    openInNewTab: "在新标签页打开",
    copyUrl: "复制URL",
    showCode: "显示代码",
    hideCode: "隐藏代码",
    variants: "变体",
    variant: "变体",
    generating: "生成中...",
    generationComplete: "生成完成",
    generationError: "生成失败",
  },

  // 侧边栏
  sidebar: {
    files: "文件",
    history: "历史",
    commits: "提交",
    console: "控制台",
    settings: "设置",
    help: "帮助",
    
    // 文件操作
    newFile: "新建文件",
    openFile: "打开文件",
    saveFile: "保存文件",
    saveAs: "另存为",
    deleteFile: "删除文件",
    renameFile: "重命名",
    
    // 历史记录
    noHistory: "暂无历史记录",
    clearHistory: "清除历史",
    restoreVersion: "恢复此版本",
  },

  // 错误消息
  errors: {
    connectionFailed: "连接失败",
    serverError: "服务器错误",
    networkError: "网络错误",
    timeout: "请求超时",
    invalidApiKey: "无效的API密钥",
    quotaExceeded: "配额已用完",
    rateLimited: "请求过于频繁，请稍后再试",
    modelNotAvailable: "所选模型不可用",
    imageUploadFailed: "图片上传失败",
    codeGenerationFailed: "代码生成失败",
    invalidImageFormat: "不支持的图片格式",
    imageTooLarge: "图片太大，请选择小于10MB的图片",
    
    websocket: {
      connectionTimeout: "连接超时",
      connectionClosed: "连接已关闭", 
      reconnecting: "正在重新连接...",
      reconnectFailed: "重连失败",
      maxRetriesReached: "已达到最大重试次数",
    },
  },

  // 提示消息
  messages: {
    welcome: "欢迎使用截图转代码！",
    betterModelAvailable: "建议使用GPT-4o或Claude 3.5 Sonnet以获得更好的效果",
    selectEditFeature: "选择和编辑功能仅支持HTML格式",
    deprecationWarning: "此功能即将弃用",
    
    // 操作提示
    uploadSuccess: "上传成功",
    generationStarted: "开始生成代码",
    generationComplete: "代码生成完成",
    codeCopied: "代码已复制到剪贴板",
    settingsSaved: "设置已保存",
    historyCleared: "历史已清除",
    
    // WebSocket状态
    connecting: "正在连接服务器...",
    connected: "已连接到服务器",
    disconnected: "与服务器断开连接",
    reconnecting: "正在重新连接...",
  },

  // 服务条款
  termsOfService: {
    title: "服务条款",
    accept: "接受",
    decline: "拒绝",
    mustAccept: "您必须接受服务条款才能继续使用",
    content: "请阅读并接受我们的服务条款...",
  },

  // 帮助和文档
  help: {
    documentation: "文档",
    tutorial: "教程",
    faq: "常见问题",
    reportIssue: "报告问题",
    contactSupport: "联系支持",
    shortcuts: "快捷键",
    
    // 快捷键
    keyboardShortcuts: {
      title: "键盘快捷键",
      generateCode: "生成代码",
      saveFile: "保存文件",
      togglePreview: "切换预览",
      toggleCode: "切换代码视图",
      undo: "撤销",
      redo: "重做",
    },
  },

  // 引导和提示
  onboarding: {
    step1Title: "上传截图",
    step1Description: "拖拽或粘贴您想要转换的界面截图",
    step2Title: "选择输出格式",
    step2Description: "选择HTML、React或其他框架",
    step3Title: "生成代码",
    step3Description: "AI将自动生成对应的代码",
    skip: "跳过引导",
    next: "下一步",
    finish: "完成",
  },
};