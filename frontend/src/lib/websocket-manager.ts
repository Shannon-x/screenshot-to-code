import {
  APP_ERROR_WEB_SOCKET_CODE,
  USER_CLOSE_WEB_SOCKET_CODE,
} from "../constants";

// WebSocket管理器配置
interface WebSocketConfig {
  reconnectDelay: number;
  maxReconnectAttempts: number;
  connectionTimeout: number;
  heartbeatInterval: number;
  heartbeatTimeout: number;
}

// 默认配置
const DEFAULT_CONFIG: WebSocketConfig = {
  reconnectDelay: 1000,
  maxReconnectAttempts: 5,
  connectionTimeout: 5000,
  heartbeatInterval: 0, // 禁用客户端心跳，因为服务端会发送
  heartbeatTimeout: 5000,
};

// 连接状态枚举
export enum ConnectionState {
  CONNECTING = "连接中",
  OPEN = "已连接",
  RECONNECTING = "重连中",
  CLOSED = "已关闭",
  ERROR = "错误",
}

// WebSocket管理器类
export class WebSocketManager {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private messageQueue: any[] = [];
  private connectionState: ConnectionState = ConnectionState.CLOSED;
  private onStateChange?: (state: ConnectionState) => void;
  private reconnecting = false;
  private lastError: string | null = null;
  
  constructor(config: Partial<WebSocketConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }
  
  // 设置状态变化回调
  public setOnStateChange(callback: (state: ConnectionState) => void) {
    this.onStateChange = callback;
  }
  
  // 获取当前连接状态
  public getState(): ConnectionState {
    return this.connectionState;
  }
  
  // 获取最后的错误信息
  public getLastError(): string | null {
    return this.lastError;
  }
  
  // 更新连接状态
  private updateState(state: ConnectionState) {
    this.connectionState = state;
    this.onStateChange?.(state);
  }
  
  // 连接到WebSocket服务器
  public connect(url: string): Promise<WebSocket> {
    return new Promise((resolve, reject) => {
      try {
        console.log(`正在连接到: ${url}`);
        this.updateState(ConnectionState.CONNECTING);
        
        this.ws = new WebSocket(url);
        
        // 设置连接超时
        const connectionTimeout = setTimeout(() => {
          if (this.ws?.readyState === WebSocket.CONNECTING) {
            this.ws.close();
            reject(new Error("连接超时"));
          }
        }, this.config.connectionTimeout);
        
        // 连接成功
        this.ws.onopen = () => {
          clearTimeout(connectionTimeout);
          console.log("WebSocket连接成功");
          this.reconnectAttempts = 0;
          this.lastError = null;
          this.updateState(ConnectionState.OPEN);
          this.processMessageQueue();
          resolve(this.ws!);
        };
        
        // 接收消息
        this.ws.onmessage = () => {
          // 消息处理将由外部处理
        };
        
        // 连接关闭
        this.ws.onclose = (event) => {
          clearTimeout(connectionTimeout);
          console.log(`WebSocket连接关闭: ${event.code} - ${event.reason}`);
          
          if (event.code === USER_CLOSE_WEB_SOCKET_CODE) {
            this.updateState(ConnectionState.CLOSED);
          } else if (event.code === APP_ERROR_WEB_SOCKET_CODE) {
            this.lastError = event.reason || "服务器错误";
            this.updateState(ConnectionState.ERROR);
          } else if (this.shouldReconnect(event.code)) {
            this.handleReconnect(url, resolve, reject);
          } else {
            this.updateState(ConnectionState.CLOSED);
          }
        };
        
        // 连接错误
        this.ws.onerror = (error) => {
          clearTimeout(connectionTimeout);
          console.error("WebSocket错误:", error);
          this.lastError = "连接错误";
          this.updateState(ConnectionState.ERROR);
        };
        
      } catch (error) {
        console.error("创建WebSocket时出错:", error);
        this.lastError = error instanceof Error ? error.message : "未知错误";
        this.updateState(ConnectionState.ERROR);
        reject(error);
      }
    });
  }
  
  // 获取WebSocket实例
  public getWebSocket(): WebSocket | null {
    return this.ws;
  }
  
  // 发送消息
  public send(data: any): boolean {
    const message = typeof data === "string" ? data : JSON.stringify(data);
    
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(message);
        return true;
      } catch (error) {
        console.error("发送消息失败:", error);
        this.messageQueue.push(data);
        return false;
      }
    } else {
      // 如果连接未就绪，将消息加入队列
      this.messageQueue.push(data);
      return false;
    }
  }
  
  // 处理消息队列
  private processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }
  
  // 关闭连接
  public close(code?: number, reason?: string) {
    this.reconnecting = false;
    if (this.ws) {
      this.ws.close(code || USER_CLOSE_WEB_SOCKET_CODE, reason);
      this.ws = null;
    }
    this.updateState(ConnectionState.CLOSED);
  }
  
  // 判断是否应该重连
  private shouldReconnect(code: number): boolean {
    // 如果正在重连或手动关闭，不再重连
    if (this.reconnecting) return false;
    
    // 以下错误码不重连
    const noReconnectCodes = [
      1000, // 正常关闭
      1001, // 端点离开
      1005, // 没有收到状态码
      USER_CLOSE_WEB_SOCKET_CODE,
      APP_ERROR_WEB_SOCKET_CODE,
    ];
    
    return !noReconnectCodes.includes(code) && 
           this.reconnectAttempts < this.config.maxReconnectAttempts;
  }
  
  // 处理重连
  private handleReconnect(url: string, resolve: Function, reject: Function) {
    if (this.reconnecting) return;
    
    this.reconnecting = true;
    this.reconnectAttempts++;
    this.updateState(ConnectionState.RECONNECTING);
    
    const delay = this.config.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    console.log(`将在 ${delay}ms 后进行第 ${this.reconnectAttempts} 次重连`);
    
    setTimeout(async () => {
      try {
        const ws = await this.connect(url);
        this.reconnecting = false;
        resolve(ws);
      } catch (error) {
        this.reconnecting = false;
        if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
          console.error("达到最大重连次数，停止重连");
          this.updateState(ConnectionState.ERROR);
          reject(error);
        }
      }
    }, delay);
  }
}

// 创建默认的WebSocket管理器实例
export const wsManager = new WebSocketManager();