import { usePersistedState } from './usePersistedState';
import { zhCN } from '../locales/zh-CN';

// 支持的语言
export enum Language {
  ZH_CN = 'zh-CN',
  EN_US = 'en-US',
}

// 英文本地化（默认）
const enUS = {
  common: {
    cancel: "Cancel",
    confirm: "Confirm",
    save: "Save",
    delete: "Delete",
    close: "Close",
    error: "Error",
    success: "Success",
    warning: "Warning",
    loading: "Loading...",
    generating: "Generating...",
    uploading: "Uploading...",
    downloading: "Downloading...",
    copied: "Copied",
    copyToClipboard: "Copy to clipboard",
    paste: "Paste",
    clear: "Clear",
    reset: "Reset",
    back: "Back",
    next: "Next",
    finish: "Finish",
    yes: "Yes",
    no: "No",
  },
  
  // 其他部分暂时保持英文
  appState: {
    initial: "Initial",
    codingInProgress: "Coding in progress",
    coding: "Coding",
    updating: "Updating",
  },
  
  inputMode: {
    image: "Image",
    video: "Video",
    text: "Text",
  },
  
  main: {
    title: "截图转代码",
    description: "Convert screenshots to clean code (HTML/Tailwind/React)",
    startTitle: "Get Started",
    uploadScreenshot: "Upload Screenshot",
    dragDropHint: "Drag & drop an image here or click to upload",
    pasteHint: "Or paste an image (Ctrl/Cmd + V)",
    generateFromText: "Generate from text",
    textPromptPlaceholder: "Describe the interface you want to create...",
    importCode: "Import Code",
    importCodePlaceholder: "Paste your existing code...",
    takeScreenshot: "Take Screenshot",
    recordVideo: "Record Video",
    stopRecording: "Stop Recording",
    createNew: "Create New",
    updateCode: "Update Code",
    regenerate: "Regenerate",
    viewHistory: "View History",
    downloadCode: "Download Code",
    shareProject: "Share Project",
  },
};

// 本地化字典
const locales = {
  [Language.ZH_CN]: zhCN,
  [Language.EN_US]: enUS,
};

// 深度获取嵌套对象的值
function getNestedValue(obj: any, path: string): string {
  return path.split('.').reduce((current, key) => current?.[key], obj) || path;
}

export function useLocale() {
  // 从本地存储获取语言设置，默认为中文
  const [language, setLanguage] = usePersistedState<Language>(
    Language.ZH_CN,
    'language'
  );

  // 获取当前语言的本地化对象
  const locale = locales[language] || locales[Language.ZH_CN];

  // t函数用于翻译
  const t = (key: string, params?: Record<string, any>): string => {
    let translation = getNestedValue(locale, key);
    
    // 如果找不到翻译，尝试英文
    if (translation === key && language !== Language.EN_US) {
      translation = getNestedValue(locales[Language.EN_US], key);
    }
    
    // 替换参数
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        translation = translation.replace(`{${key}}`, String(value));
      });
    }
    
    return translation;
  };

  return {
    t,
    language,
    setLanguage,
    languages: Object.values(Language),
  };
}