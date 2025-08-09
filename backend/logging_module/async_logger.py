"""
Async Logging System - High-performance asynchronous logging
"""
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
from enum import Enum
import aiofiles
from contextlib import asynccontextmanager
import traceback

class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AsyncLogger:
    """
    Asynchronous logger with queue-based buffering for high performance.
    Features:
    - Non-blocking logging operations
    - Batch writes for efficiency
    - Structured logging support
    - Multiple output targets
    - Automatic log rotation
    """
    
    def __init__(
        self,
        name: str,
        log_dir: str = "logs",
        max_queue_size: int = 10000,
        batch_size: int = 100,
        flush_interval: float = 1.0,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.max_queue_size = max_queue_size
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._flush_task: Optional[asyncio.Task] = None
        self._file_path = self.log_dir / f"{name}.log"
        self._current_file_size = 0
        
        # Setup standard logger for fallback
        self._fallback_logger = logging.getLogger(name)
        self._fallback_logger.setLevel(logging.DEBUG)
        
        # Add console handler if not exists
        if not self._fallback_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            )
            self._fallback_logger.addHandler(handler)
    
    async def start(self):
        """Start the async logger"""
        if not self._flush_task:
            self._flush_task = asyncio.create_task(self._flush_loop())
            await self.info("Async logger started", {"logger_name": self.name})
    
    async def stop(self):
        """Stop the async logger and flush remaining logs"""
        if self._flush_task:
            # Flush remaining logs
            await self._flush_batch()
            
            # Cancel flush task
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
            
            await self.info("Async logger stopped", {"logger_name": self.name})
    
    async def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        await self._log(LogLevel.DEBUG, message, extra)
    
    async def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message"""
        await self._log(LogLevel.INFO, message, extra)
    
    async def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        await self._log(LogLevel.WARNING, message, extra)
    
    async def error(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log error message"""
        if exc_info:
            extra = extra or {}
            extra["traceback"] = traceback.format_exc()
        await self._log(LogLevel.ERROR, message, extra)
    
    async def critical(self, message: str, extra: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """Log critical message"""
        if exc_info:
            extra = extra or {}
            extra["traceback"] = traceback.format_exc()
        await self._log(LogLevel.CRITICAL, message, extra)
    
    async def _log(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None):
        """Internal log method"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.value,
            "logger": self.name,
            "message": message,
            "extra": extra or {}
        }
        
        try:
            # Try to add to queue (non-blocking)
            self._queue.put_nowait(log_entry)
        except asyncio.QueueFull:
            # Fallback to standard logger if queue is full
            self._fallback_logger.log(
                getattr(logging, level.value),
                f"{message} | {json.dumps(extra or {})}"
            )
    
    async def _flush_loop(self):
        """Background task to flush logs periodically"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._fallback_logger.error(f"Error in flush loop: {e}")
    
    async def _flush_batch(self):
        """Flush a batch of logs to file"""
        if self._queue.empty():
            return
        
        batch = []
        try:
            # Collect batch
            for _ in range(min(self.batch_size, self._queue.qsize())):
                try:
                    log_entry = self._queue.get_nowait()
                    batch.append(log_entry)
                except asyncio.QueueEmpty:
                    break
            
            if batch:
                await self._write_batch(batch)
        except Exception as e:
            self._fallback_logger.error(f"Error flushing batch: {e}")
    
    async def _write_batch(self, batch: list):
        """Write a batch of logs to file"""
        # Check if rotation is needed
        await self._check_rotation()
        
        # Format logs
        lines = []
        for entry in batch:
            # Format as JSON for structured logging
            line = json.dumps(entry, ensure_ascii=False) + "\n"
            lines.append(line)
            self._current_file_size += len(line.encode('utf-8'))
        
        # Write to file
        async with aiofiles.open(self._file_path, 'a', encoding='utf-8') as f:
            await f.writelines(lines)
    
    async def _check_rotation(self):
        """Check if log rotation is needed"""
        if not self._file_path.exists():
            self._current_file_size = 0
            return
        
        # Get current file size if not tracked
        if self._current_file_size == 0:
            self._current_file_size = self._file_path.stat().st_size
        
        # Rotate if needed
        if self._current_file_size >= self.max_file_size:
            await self._rotate_logs()
    
    async def _rotate_logs(self):
        """Rotate log files"""
        # Move existing backups
        for i in range(self.backup_count - 1, 0, -1):
            old_backup = self.log_dir / f"{self.name}.log.{i}"
            new_backup = self.log_dir / f"{self.name}.log.{i + 1}"
            if old_backup.exists():
                old_backup.rename(new_backup)
        
        # Move current log to backup 1
        if self._file_path.exists():
            backup_1 = self.log_dir / f"{self.name}.log.1"
            self._file_path.rename(backup_1)
        
        # Reset file size counter
        self._current_file_size = 0

class AsyncLoggerManager:
    """Manager for multiple async loggers"""
    
    def __init__(self):
        self._loggers: Dict[str, AsyncLogger] = {}
        self._started = False
    
    def get_logger(self, name: str, **kwargs) -> AsyncLogger:
        """Get or create a logger"""
        if name not in self._loggers:
            self._loggers[name] = AsyncLogger(name, **kwargs)
            if self._started:
                # Start logger if manager is already started
                asyncio.create_task(self._loggers[name].start())
        return self._loggers[name]
    
    async def start_all(self):
        """Start all loggers"""
        for logger in self._loggers.values():
            await logger.start()
        self._started = True
    
    async def stop_all(self):
        """Stop all loggers"""
        for logger in self._loggers.values():
            await logger.stop()
        self._started = False

# Global logger manager
logger_manager = AsyncLoggerManager()

# Convenience functions
def get_logger(name: str, **kwargs) -> AsyncLogger:
    """Get an async logger instance"""
    return logger_manager.get_logger(name, **kwargs)

# Context manager for automatic start/stop
@asynccontextmanager
async def async_logger_context():
    """Context manager for async logging"""
    await logger_manager.start_all()
    try:
        yield logger_manager
    finally:
        await logger_manager.stop_all()

# Integration with standard logging
class AsyncLoggingHandler(logging.Handler):
    """
    Handler to bridge standard logging to async logging
    """
    
    def __init__(self, async_logger: AsyncLogger):
        super().__init__()
        self.async_logger = async_logger
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record"""
        # Convert log level
        level_map = {
            logging.DEBUG: LogLevel.DEBUG,
            logging.INFO: LogLevel.INFO,
            logging.WARNING: LogLevel.WARNING,
            logging.ERROR: LogLevel.ERROR,
            logging.CRITICAL: LogLevel.CRITICAL
        }
        
        level = level_map.get(record.levelno, LogLevel.INFO)
        
        # Extract extra data
        extra = {
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
            "pathname": record.pathname
        }
        
        # Add any extra attributes
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 
                          'funcName', 'levelname', 'levelno', 'lineno', 
                          'module', 'msecs', 'pathname', 'process', 
                          'processName', 'relativeCreated', 'thread', 
                          'threadName', 'exc_info', 'exc_text', 'stack_info']:
                extra[key] = value
        
        # Schedule async log
        try:
            asyncio.create_task(
                self.async_logger._log(level, record.getMessage(), extra)
            )
        except RuntimeError:
            # No event loop, use fallback
            self.async_logger._fallback_logger.log(record.levelno, record.getMessage())