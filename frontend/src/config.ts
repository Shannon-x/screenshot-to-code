// Default to false if set to anything other than "true" or unset
export const IS_RUNNING_ON_CLOUD =
  import.meta.env.VITE_IS_DEPLOYED === "true" || false;

// 智能选择WebSocket协议：处理容器环境和浏览器环境
function getWebSocketURL(): string {
  const envURL = import.meta.env.VITE_WS_BACKEND_URL;
  
  if (envURL) {
    // 如果是浏览器环境，需要使用当前页面的协议和域名
    if (typeof window !== 'undefined') {
      // 开发环境：localhost访问
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return envURL;
      }
      
      // 生产环境：使用当前页面的协议和域名（同源）
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      return `${protocol}//${host}/generate-code`;
    }
    
    // 服务器端渲染或构建时使用环境变量
    return envURL;
  }
  
  // 默认值处理
  if (typeof window !== 'undefined') {
    // 浏览器环境
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    
    // 如果是localhost开发环境，使用默认端口
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return `${protocol === 'wss:' ? 'ws:' : protocol}//127.0.0.1:7001`;
    }
    
    // 生产环境使用当前域名
    return `${protocol}//${host}/generate-code`;
  }
  
  return "ws://backend:7001"; // 容器内部通信
}

export const WS_BACKEND_URL = getWebSocketURL();

// 同样处理HTTP后端URL
function getHTTPURL(): string {
  const envURL = import.meta.env.VITE_HTTP_BACKEND_URL;
  
  if (envURL) {
    // 如果是浏览器环境，需要使用当前页面的协议和域名
    if (typeof window !== 'undefined') {
      // 开发环境：localhost访问
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return envURL;
      }
      
      // 生产环境：使用当前页面的协议和域名（同源）
      const protocol = window.location.protocol;
      const host = window.location.host;
      return `${protocol}//${host}/api`;
    }
    
    // 服务器端渲染或构建时使用环境变量
    return envURL;
  }
  
  // 默认值处理
  if (typeof window !== 'undefined') {
    // 浏览器环境
    const protocol = window.location.protocol;
    const host = window.location.host;
    
    // 如果是localhost开发环境，使用默认端口
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return `${protocol === 'https:' ? 'http:' : protocol}//127.0.0.1:7001`;
    }
    
    // 生产环境使用当前域名
    return `${protocol}//${host}/api`;
  }
  
  return "http://backend:7001"; // 容器内部通信
}

export const HTTP_BACKEND_URL = getHTTPURL();

export const PICO_BACKEND_FORM_SECRET =
  import.meta.env.VITE_PICO_BACKEND_FORM_SECRET || null;
