// Default to false if set to anything other than "true" or unset
export const IS_RUNNING_ON_CLOUD =
  import.meta.env.VITE_IS_DEPLOYED === "true" || false;

// 智能选择WebSocket协议：处理混合内容问题的多种方案
function getWebSocketURL(): string {
  const envURL = import.meta.env.VITE_WS_BACKEND_URL;
  
  if (envURL) {
    // 开发环境：直接使用环境变量
    if (typeof window === 'undefined' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return envURL;
    }
    
    // 生产环境HTTPS：尝试多种方案
    if (window.location.protocol === 'https:') {
      // 方案1: 尝试使用相同域名的WebSocket (推荐)
      const currentHost = window.location.host;
      const wsPath = '/generate-code';
      const sameOriginWS = `wss://${currentHost}${wsPath}`;
      
      // 如果环境变量指向当前域名，使用安全的wss://
      if (envURL.includes(currentHost)) {
        return sameOriginWS;
      }
      
      // 方案2: 如果后端支持WSS，转换协议
      const wssUrl = envURL.replace(/^ws:\/\//, 'wss://');
      return wssUrl;
    }
    
    return envURL;
  }
  
  // 默认值处理
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    return "wss://127.0.0.1:7001";
  }
  return "ws://127.0.0.1:7001";
}

export const WS_BACKEND_URL = getWebSocketURL();

// 同样处理HTTP后端URL
function getHTTPURL(): string {
  const envURL = import.meta.env.VITE_HTTP_BACKEND_URL;
  
  if (envURL) {
    // 开发环境：直接使用环境变量
    if (typeof window === 'undefined' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return envURL;
    }
    
    // 生产环境HTTPS：使用同域名或转换协议
    if (window.location.protocol === 'https:') {
      const currentHost = window.location.host;
      
      // 如果环境变量指向当前域名，使用安全的https://
      if (envURL.includes(currentHost)) {
        return `https://${currentHost}`;
      }
      
      // 转换协议
      return envURL.replace(/^http:\/\//, 'https://');
    }
    
    return envURL;
  }
  
  // 默认值处理
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    return "https://127.0.0.1:7001";
  }
  return "http://127.0.0.1:7001";
}

export const HTTP_BACKEND_URL = getHTTPURL();

export const PICO_BACKEND_FORM_SECRET =
  import.meta.env.VITE_PICO_BACKEND_FORM_SECRET || null;
