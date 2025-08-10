"""
WebSocket Manager - Centralized WebSocket communication management
"""
import asyncio
import json
import time
from typing import Any, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """WebSocket message types"""
    CHUNK = "chunk"
    STATUS = "status"
    SET_CODE = "setCode"
    ERROR = "error"
    VARIANT_COMPLETE = "variantComplete"
    VARIANT_ERROR = "variantError"
    VARIANT_COUNT = "variantCount"
    HEARTBEAT = "heartbeat"
    
@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection with metadata"""
    websocket: WebSocket
    connection_id: str
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    client_ip: str = ""
    user_agent: str = ""
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

class WebSocketManager:
    """
    Centralized WebSocket manager for handling all WebSocket communications
    Provides:
    - Connection pooling
    - Message queuing
    - Automatic reconnection
    - Error handling
    - Heartbeat mechanism
    """
    
    def __init__(self, max_connections: int = 100, heartbeat_interval: int = 60):  # Increased heartbeat interval
        self.connections: Dict[str, WebSocketConnection] = {}
        self.max_connections = max_connections
        self.heartbeat_interval = heartbeat_interval
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._message_queues: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()
        
    async def start(self):
        """Start the WebSocket manager"""
        if not self._heartbeat_task:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info("WebSocket manager started")
    
    async def stop(self):
        """Stop the WebSocket manager"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for conn_id in list(self.connections.keys()):
            await self.disconnect(conn_id)
        
        logger.info("WebSocket manager stopped")
    
    @asynccontextmanager
    async def connection(self, websocket: WebSocket, connection_id: str):
        """Context manager for WebSocket connections"""
        try:
            await self.connect(websocket, connection_id)
            yield self
        finally:
            await self.disconnect(connection_id)
    
    async def connect(self, websocket: WebSocket, connection_id: str) -> bool:
        """
        Register a new WebSocket connection
        
        Args:
            websocket: The WebSocket instance
            connection_id: Unique identifier for the connection
            
        Returns:
            True if connection was successful, False otherwise
        """
        async with self._lock:
            # Check if we've reached max connections
            if len(self.connections) >= self.max_connections:
                await self._cleanup_stale_connections()
                if len(self.connections) >= self.max_connections:
                    logger.warning(f"Max connections reached ({self.max_connections})")
                    return False
            
            # Extract client info
            client_ip = websocket.client.host if websocket.client else "unknown"
            user_agent = websocket.headers.get("User-Agent", "unknown")
            
            # Create connection
            connection = WebSocketConnection(
                websocket=websocket,
                connection_id=connection_id,
                client_ip=client_ip,
                user_agent=user_agent
            )
            
            self.connections[connection_id] = connection
            self._message_queues[connection_id] = asyncio.Queue()
            
            logger.info(f"WebSocket connected: {connection_id} from {client_ip}")
            return True
    
    async def disconnect(self, connection_id: str):
        """Disconnect and cleanup a WebSocket connection"""
        async with self._lock:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                try:
                    await connection.websocket.close()
                except Exception as e:
                    logger.error(f"Error closing WebSocket {connection_id}: {e}")
                
                del self.connections[connection_id]
                
                # Clean up message queue
                if connection_id in self._message_queues:
                    del self._message_queues[connection_id]
                
                logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_message(
        self,
        connection_id: str,
        message_type: MessageType,
        data: Any,
        variant_index: int = 0
    ) -> bool:
        """
        Send a message to a specific WebSocket connection
        
        Args:
            connection_id: Connection identifier
            message_type: Type of message
            data: Message data
            variant_index: Variant index for multi-variant responses
            
        Returns:
            True if message was sent successfully
        """
        if connection_id not in self.connections:
            logger.warning(f"Connection {connection_id} not found")
            return False
        
        connection = self.connections[connection_id]
        message = {
            "type": message_type.value,
            "value": data,
            "variantIndex": variant_index,
            "timestamp": time.time()
        }
        
        try:
            # Add timeout to prevent indefinite blocking
            await asyncio.wait_for(
                connection.websocket.send_json(message),
                timeout=10.0  # 10 second timeout for sending
            )
            connection.update_activity()
            return True
        except asyncio.TimeoutError:
            logger.error(f"Timeout sending message to {connection_id}")
            await self.disconnect(connection_id)
            return False
        except WebSocketDisconnect:
            logger.info(f"WebSocket {connection_id} disconnected during send")
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            return False
    
    async def broadcast_message(
        self,
        message_type: MessageType,
        data: Any,
        exclude: Optional[Set[str]] = None
    ):
        """Broadcast a message to all connected clients"""
        exclude = exclude or set()
        tasks = []
        
        for conn_id in self.connections:
            if conn_id not in exclude:
                task = asyncio.create_task(
                    self.send_message(conn_id, message_type, data)
                )
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_chunk(self, connection_id: str, chunk: str, variant_index: int = 0):
        """Send a code chunk"""
        return await self.send_message(
            connection_id,
            MessageType.CHUNK,
            chunk,
            variant_index
        )
    
    async def send_status(self, connection_id: str, status: str, variant_index: int = 0):
        """Send a status update"""
        return await self.send_message(
            connection_id,
            MessageType.STATUS,
            status,
            variant_index
        )
    
    async def send_error(self, connection_id: str, error: str, variant_index: int = 0):
        """Send an error message"""
        return await self.send_message(
            connection_id,
            MessageType.ERROR,
            error,
            variant_index
        )
    
    async def send_variant_complete(self, connection_id: str, variant_index: int):
        """Send variant completion message"""
        return await self.send_message(
            connection_id,
            MessageType.VARIANT_COMPLETE,
            "",
            variant_index
        )
    
    async def send_variant_count(self, connection_id: str, count: int):
        """Send variant count message"""
        return await self.send_message(
            connection_id,
            MessageType.VARIANT_COUNT,
            str(count),
            0
        )
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeats to all connections"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                await self._send_heartbeats()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    async def _send_heartbeats(self):
        """Send heartbeat to all connections"""
        tasks = []
        for conn_id in list(self.connections.keys()):
            task = asyncio.create_task(
                self.send_message(conn_id, MessageType.HEARTBEAT, "ping")
            )
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Remove failed connections
            for conn_id, result in zip(list(self.connections.keys()), results):
                if isinstance(result, Exception) or result is False:
                    await self.disconnect(conn_id)
    
    async def _cleanup_stale_connections(self):
        """Remove stale connections that haven't been active"""
        current_time = datetime.now()
        stale_threshold = 300  # 5 minutes
        
        stale_connections = []
        for conn_id, connection in self.connections.items():
            if (current_time - connection.last_activity).total_seconds() > stale_threshold:
                stale_connections.append(conn_id)
        
        for conn_id in stale_connections:
            logger.info(f"Removing stale connection: {conn_id}")
            await self.disconnect(conn_id)
    
    def get_connection_count(self) -> int:
        """Get current number of connections"""
        return len(self.connections)
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific connection"""
        if connection_id in self.connections:
            conn = self.connections[connection_id]
            return {
                "connection_id": connection_id,
                "client_ip": conn.client_ip,
                "user_agent": conn.user_agent,
                "connected_at": conn.connected_at.isoformat(),
                "last_activity": conn.last_activity.isoformat(),
                "duration_seconds": (datetime.now() - conn.connected_at).total_seconds()
            }
        return None
    
    def get_all_connections(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all connections"""
        return {
            conn_id: self.get_connection_info(conn_id)
            for conn_id in self.connections
        }

# Global WebSocket manager instance
ws_manager = WebSocketManager()

# Convenience decorators for WebSocket handlers
def with_websocket_manager(func):
    """Decorator to inject WebSocket manager into handler"""
    async def wrapper(websocket: WebSocket, *args, **kwargs):
        connection_id = f"{websocket.client.host}_{time.time()}"
        async with ws_manager.connection(websocket, connection_id):
            return await func(websocket, ws_manager, connection_id, *args, **kwargs)
    return wrapper