import toast from "react-hot-toast";
import { WS_BACKEND_URL } from "./config";
import {
  APP_ERROR_WEB_SOCKET_CODE,
  USER_CLOSE_WEB_SOCKET_CODE,
} from "./constants";
import { FullGenerationSettings } from "./types";
import { WebSocketManager, ConnectionState } from "./lib/websocket-manager";

const ERROR_MESSAGE =
  "生成代码时出错。请检查开发者控制台和后端日志以获取详细信息。如有需要，请在 Github 上提交问题。";

const CANCEL_MESSAGE = "代码生成已取消";

type WebSocketResponse = {
  type:
    | "chunk"
    | "status"
    | "setCode"
    | "error"
    | "variantComplete"
    | "variantError"
    | "variantCount"
    | "pong"  // 添加心跳响应类型
    | "heartbeat";  // 后端发送的心跳消息
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
  onConnectionStateChange?: (state: ConnectionState) => void;
}

// 生成WebSocket URL
function generateWebSocketUrl(): string {
  // 如果配置的URL已经包含完整路径，直接使用
  if (WS_BACKEND_URL.includes('/generate-code')) {
    return WS_BACKEND_URL;
  }
  
  // 否则添加端点路径
  const baseUrl = WS_BACKEND_URL.endsWith('/') 
    ? WS_BACKEND_URL.slice(0, -1) 
    : WS_BACKEND_URL;
    
  return `${baseUrl}/generate-code`;
}

export async function generateCode(
  wsRef: React.MutableRefObject<WebSocket | null>,
  params: FullGenerationSettings,
  callbacks: CodeGenerationCallbacks
) {
  // 创建WebSocket管理器实例
  const wsManager = new WebSocketManager({
    reconnectDelay: 2000,
    maxReconnectAttempts: 3,
    connectionTimeout: 15000,
    heartbeatInterval: 30000,
    heartbeatTimeout: 5000,
  });

  // 设置连接状态变化回调
  wsManager.setOnStateChange((state) => {
    console.log(`WebSocket状态: ${state}`);
    if (callbacks.onConnectionStateChange) {
      callbacks.onConnectionStateChange(state);
    }
    
    // 根据状态显示提示
    switch (state) {
      case ConnectionState.CONNECTING:
        toast.loading("正在连接服务器...", { id: "ws-connecting" });
        break;
      case ConnectionState.OPEN:
        toast.success("已连接到服务器", { id: "ws-connecting" });
        break;
      case ConnectionState.RECONNECTING:
        toast.loading("正在重新连接...", { id: "ws-reconnecting" });
        break;
      case ConnectionState.ERROR:
        toast.dismiss("ws-connecting");
        toast.dismiss("ws-reconnecting");
        const errorMsg = wsManager.getLastError() || "连接错误";
        toast.error(`连接失败: ${errorMsg}`);
        callbacks.onCancel();
        break;
      case ConnectionState.CLOSED:
        toast.dismiss("ws-connecting");
        toast.dismiss("ws-reconnecting");
        break;
    }
  });

  try {
    // 建立连接
    const wsUrl = generateWebSocketUrl();
    console.log("WebSocket URL:", wsUrl);
    
    const ws = await wsManager.connect(wsUrl);
    wsRef.current = ws;
    
    // 设置消息处理器
    ws.onmessage = async (event: MessageEvent) => {
      try {
        const response = JSON.parse(event.data) as WebSocketResponse;
        
        // 处理不同类型的消息
        switch (response.type) {
          case "chunk":
            callbacks.onChange(response.value, response.variantIndex);
            break;
          case "status":
            callbacks.onStatusUpdate(response.value, response.variantIndex);
            break;
          case "setCode":
            callbacks.onSetCode(response.value, response.variantIndex);
            break;
          case "variantComplete":
            callbacks.onVariantComplete(response.variantIndex);
            break;
          case "variantError":
            callbacks.onVariantError(response.variantIndex, response.value);
            break;
          case "variantCount":
            callbacks.onVariantCount(parseInt(response.value));
            break;
          case "error":
            console.error("生成代码时出错:", response.value);
            toast.error(response.value);
            break;
          case "heartbeat":
            // 心跳消息，发送pong响应
            ws.send(JSON.stringify({ type: 'pong' }));
            break;
          default:
            console.warn("未知的消息类型:", response.type);
        }
      } catch (error) {
        console.error("处理WebSocket消息时出错:", error);
      }
    };
    
    // 重写关闭处理器以使用我们的回调
    ws.onclose = (event) => {
      console.log(`WebSocket连接关闭: ${event.code} - ${event.reason}`);
      
      if (event.code === USER_CLOSE_WEB_SOCKET_CODE) {
        toast.success(CANCEL_MESSAGE);
        callbacks.onCancel();
      } else if (event.code === APP_ERROR_WEB_SOCKET_CODE) {
        console.error("服务器错误", event);
        callbacks.onCancel();
      } else if (event.code === 1000) {
        // 正常关闭
        callbacks.onComplete();
      }
    };
    
    // 发送参数
    const sendSuccess = wsManager.send(params);
    if (!sendSuccess) {
      throw new Error("发送参数失败");
    }
    
  } catch (error) {
    console.error("WebSocket连接失败:", error);
    
    // 根据错误类型显示不同的提示
    const isHttps = window.location.protocol === 'https:';
    if (isHttps && error instanceof Error && error.message.includes('连接超时')) {
      toast.error(
        "无法建立安全的WebSocket连接。请确保：\n" +
        "1. 后端服务器支持WSS (SSL/TLS)\n" +
        "2. 或者配置反向代理转发WebSocket连接\n" +
        "3. 或者使用HTTP版本的网站",
        { duration: 8000 }
      );
    } else {
      toast.error(ERROR_MESSAGE);
    }
    
    callbacks.onCancel();
  }
}

// 导出关闭WebSocket的函数
export function closeWebSocket(ws: WebSocket | null) {
  if (ws && ws.readyState !== WebSocket.CLOSED) {
    ws.close(USER_CLOSE_WEB_SOCKET_CODE, "用户取消");
  }
}