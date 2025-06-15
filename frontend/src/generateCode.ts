import toast from "react-hot-toast";
import { WS_BACKEND_URL } from "./config";
import {
  APP_ERROR_WEB_SOCKET_CODE,
  USER_CLOSE_WEB_SOCKET_CODE,
} from "./constants";
import { FullGenerationSettings } from "./types";

const ERROR_MESSAGE =
  "Error generating code. Check the Developer Console AND the backend logs for details. Feel free to open a Github issue.";

const CANCEL_MESSAGE = "Code generation cancelled";

type WebSocketResponse = {
  type:
    | "chunk"
    | "status"
    | "setCode"
    | "error"
    | "variantComplete"
    | "variantError"
    | "variantCount";
  value: string;
  variantIndex: number;
};

interface CodeGenerationCallbacks {
  onChange: (chunk: string, variantIndex: number) => void;
  onSetCode: (code: string, variantIndex: number) => void;
  onStatusUpdate: (status: string, variantIndex: number) => void;
  onVariantComplete: (variantIndex: number) => void;
  onVariantError: (variantIndex: number, error: string) => void;
  onVariantCount: (count: number) => void;
  onCancel: () => void;
  onComplete: () => void;
}

// 生成可能的WebSocket URL列表（按优先级排序）
function generateWebSocketUrls(baseUrl: string): string[] {
  const urls: string[] = [];
  
  // 如果是HTTPS环境，尝试多种方案
  if (typeof window !== 'undefined' && window.location.protocol === 'https:') {
    // 方案1: 使用当前域名的WebSocket代理
    const currentHost = window.location.host;
    urls.push(`wss://${currentHost}/generate-code`);
    
    // 方案2: 如果原URL是ws://，尝试转换为wss://
    if (baseUrl.startsWith('ws://')) {
      const wssUrl = baseUrl.replace(/^ws:\/\//, 'wss://');
      urls.push(wssUrl);
    } else {
      urls.push(baseUrl);
    }
    
    // 方案3: 显示用户友好的错误信息，不自动回退到不安全连接
  } else {
    // 非HTTPS环境，直接使用原URL
    urls.push(baseUrl);
  }
  
  return urls;
}

export function generateCode(
  wsRef: React.MutableRefObject<WebSocket | null>,
  params: FullGenerationSettings,
  callbacks: CodeGenerationCallbacks
) {
  // WS_BACKEND_URL 已经包含了正确的端点，不需要再添加 /generate-code
  let baseWsUrl = WS_BACKEND_URL;
  
  // 只有在开发环境或者URL不包含 /generate-code 时才添加路径
  if (typeof window !== 'undefined' && 
      (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') &&
      !baseWsUrl.includes('/generate-code')) {
    baseWsUrl = `${baseWsUrl}/generate-code`;
  }
  
  const possibleUrls = generateWebSocketUrls(baseWsUrl);
  
  console.log("Possible WebSocket URLs:", possibleUrls);
  
  // 尝试连接到第一个URL
  tryConnectToWebSocket(possibleUrls, 0, wsRef, params, callbacks);
}

function tryConnectToWebSocket(
  urls: string[],
  currentIndex: number,
  wsRef: React.MutableRefObject<WebSocket | null>,
  params: FullGenerationSettings,
  callbacks: CodeGenerationCallbacks
) {
  if (currentIndex >= urls.length) {
    // 所有URL都失败了
    const isHttps = typeof window !== 'undefined' && window.location.protocol === 'https:';
    if (isHttps) {
      toast.error(
        "无法建立安全的WebSocket连接。请确保：\n" +
        "1. 后端服务器支持WSS (SSL/TLS)\n" +
        "2. 或者配置反向代理转发WebSocket连接\n" +
        "3. 或者使用HTTP版本的网站"
      );
    } else {
      toast.error(ERROR_MESSAGE);
    }
    callbacks.onCancel();
    return;
  }
  
  const wsUrl = urls[currentIndex];
  console.log(`Attempting to connect to: ${wsUrl} (attempt ${currentIndex + 1}/${urls.length})`);
  
  const ws = new WebSocket(wsUrl);
  wsRef.current = ws;
  
  // 设置连接超时
  const connectionTimeout = setTimeout(() => {
    if (ws.readyState === WebSocket.CONNECTING) {
      console.log(`Connection timeout for ${wsUrl}`);
      ws.close();
    }
  }, 5000); // 5秒超时
  
  ws.addEventListener("open", () => {
    clearTimeout(connectionTimeout);
    console.log(`Successfully connected to: ${wsUrl}`);
    ws.send(JSON.stringify(params));
  });

  ws.addEventListener("message", async (event: MessageEvent) => {
    const response = JSON.parse(event.data) as WebSocketResponse;
    if (response.type === "chunk") {
      callbacks.onChange(response.value, response.variantIndex);
    } else if (response.type === "status") {
      callbacks.onStatusUpdate(response.value, response.variantIndex);
    } else if (response.type === "setCode") {
      callbacks.onSetCode(response.value, response.variantIndex);
    } else if (response.type === "variantComplete") {
      callbacks.onVariantComplete(response.variantIndex);
    } else if (response.type === "variantError") {
      callbacks.onVariantError(response.variantIndex, response.value);
    } else if (response.type === "variantCount") {
      callbacks.onVariantCount(parseInt(response.value));
    } else if (response.type === "error") {
      console.error("Error generating code", response.value);
      toast.error(response.value);
    }
  });

  ws.addEventListener("close", (event) => {
    clearTimeout(connectionTimeout);
    console.log(`Connection closed for ${wsUrl}`, event.code, event.reason);
    
    if (event.code === USER_CLOSE_WEB_SOCKET_CODE) {
      toast.success(CANCEL_MESSAGE);
      callbacks.onCancel();
    } else if (event.code === APP_ERROR_WEB_SOCKET_CODE) {
      console.error("Known server error", event);
      callbacks.onCancel();
    } else if (event.code !== 1000) {
      // 连接失败，尝试下一个URL
      if (currentIndex + 1 < urls.length) {
        console.log(`Trying next WebSocket URL...`);
        tryConnectToWebSocket(urls, currentIndex + 1, wsRef, params, callbacks);
      } else {
        console.error("All WebSocket URLs failed", event);
        const isHttps = typeof window !== 'undefined' && window.location.protocol === 'https:';
        if (isHttps) {
          toast.error(
            "WebSocket连接失败。这通常是因为：\n" +
            "• 后端服务器不支持WSS (需要SSL证书)\n" +
            "• 需要配置反向代理来处理WebSocket连接\n" +
            "建议联系系统管理员配置SSL证书或代理"
          );
        } else {
          toast.error(ERROR_MESSAGE);
        }
        callbacks.onCancel();
      }
    } else {
      callbacks.onComplete();
    }
  });

  ws.addEventListener("error", (error) => {
    clearTimeout(connectionTimeout);
    console.error(`WebSocket error for ${wsUrl}:`, error);
    
    // 如果还有其他URL可以尝试，不显示错误消息
    if (currentIndex + 1 >= urls.length) {
      toast.error(ERROR_MESSAGE);
    }
  });
}
