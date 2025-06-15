// Default to false if set to anything other than "true" or unset
export const IS_RUNNING_ON_CLOUD =
  import.meta.env.VITE_IS_DEPLOYED === "true" || false;

// 智能选择WebSocket协议：如果当前页面是HTTPS，自动使用WSS
function getWebSocketURL(): string {
  const envURL = import.meta.env.VITE_WS_BACKEND_URL;
  
  if (envURL) {
    // 如果设置了环境变量，检查当前页面是否为HTTPS
    if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
      // 如果当前页面是HTTPS，但环境变量是ws://，自动转换为wss://
      return envURL.replace(/^ws:\/\//, 'wss://');
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
    // 如果设置了环境变量，检查当前页面是否为HTTPS
    if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
      // 如果当前页面是HTTPS，但环境变量是http://，自动转换为https://
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
