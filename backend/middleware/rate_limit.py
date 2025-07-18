from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import asyncio
from collections import defaultdict
import os

class RateLimiter:
    """
    Simple rate limiter implementation using token bucket algorithm.
    In production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 300,
        burst_size: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        
        # Storage for rate limit data (use Redis in production)
        self.minute_buckets: Dict[str, Dict[str, any]] = defaultdict(lambda: {
            "tokens": self.requests_per_minute,
            "last_update": time.time()
        })
        
        self.hour_buckets: Dict[str, Dict[str, any]] = defaultdict(lambda: {
            "count": 0,
            "reset_time": datetime.now() + timedelta(hours=1)
        })
        
        # WebSocket-specific limits
        self.ws_connections: Dict[str, int] = defaultdict(int)
        self.max_ws_connections_per_ip = 5
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_task())
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP if there are multiple
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def _refill_tokens(self, bucket: Dict[str, any], rate: int) -> None:
        """Refill tokens based on time elapsed"""
        now = time.time()
        time_passed = now - bucket["last_update"]
        
        # Add tokens based on time passed
        tokens_to_add = time_passed * (rate / 60.0)
        bucket["tokens"] = min(rate, bucket["tokens"] + tokens_to_add)
        bucket["last_update"] = now
    
    async def check_rate_limit(self, request: Request) -> bool:
        """Check if request should be rate limited"""
        client_ip = self._get_client_ip(request)
        
        # Skip rate limiting for localhost in development
        if not os.environ.get("IS_PROD") and client_ip in ["127.0.0.1", "localhost", "::1"]:
            return True
        
        # Check minute rate limit
        minute_bucket = self.minute_buckets[client_ip]
        self._refill_tokens(minute_bucket, self.requests_per_minute)
        
        if minute_bucket["tokens"] < 1:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )
        
        # Check hourly rate limit
        hour_bucket = self.hour_buckets[client_ip]
        if datetime.now() > hour_bucket["reset_time"]:
            hour_bucket["count"] = 0
            hour_bucket["reset_time"] = datetime.now() + timedelta(hours=1)
        
        if hour_bucket["count"] >= self.requests_per_hour:
            retry_after = int((hour_bucket["reset_time"] - datetime.now()).total_seconds())
            raise HTTPException(
                status_code=429,
                detail=f"Hourly rate limit exceeded. Reset in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )
        
        # Consume tokens
        minute_bucket["tokens"] -= 1
        hour_bucket["count"] += 1
        
        return True
    
    def check_websocket_limit(self, client_ip: str) -> bool:
        """Check if client can open a new WebSocket connection"""
        if not os.environ.get("IS_PROD") and client_ip in ["127.0.0.1", "localhost", "::1"]:
            return True
        
        if self.ws_connections[client_ip] >= self.max_ws_connections_per_ip:
            return False
        
        return True
    
    def add_websocket_connection(self, client_ip: str) -> None:
        """Register a new WebSocket connection"""
        self.ws_connections[client_ip] += 1
    
    def remove_websocket_connection(self, client_ip: str) -> None:
        """Remove a WebSocket connection"""
        if client_ip in self.ws_connections:
            self.ws_connections[client_ip] = max(0, self.ws_connections[client_ip] - 1)
            if self.ws_connections[client_ip] == 0:
                del self.ws_connections[client_ip]
    
    async def _cleanup_task(self) -> None:
        """Periodic cleanup of old rate limit data"""
        while True:
            try:
                # Clean up old minute buckets
                current_time = time.time()
                expired_ips = []
                
                for ip, bucket in self.minute_buckets.items():
                    # Remove buckets not used for more than 5 minutes
                    if current_time - bucket["last_update"] > 300:
                        expired_ips.append(ip)
                
                for ip in expired_ips:
                    del self.minute_buckets[ip]
                
                # Clean up old hour buckets
                now = datetime.now()
                expired_hour_ips = []
                
                for ip, bucket in self.hour_buckets.items():
                    # Remove buckets past their reset time by more than 1 hour
                    if now > bucket["reset_time"] + timedelta(hours=1):
                        expired_hour_ips.append(ip)
                
                for ip in expired_hour_ips:
                    del self.hour_buckets[ip]
                
                # Wait 5 minutes before next cleanup
                await asyncio.sleep(300)
                
            except Exception as e:
                print(f"Error in rate limiter cleanup: {e}")
                await asyncio.sleep(60)


# Create global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_minute=int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60")),
    requests_per_hour=int(os.environ.get("RATE_LIMIT_PER_HOUR", "300")),
    burst_size=int(os.environ.get("RATE_LIMIT_BURST_SIZE", "10"))
)


async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware for rate limiting"""
    try:
        # Check rate limit
        await rate_limiter.check_rate_limit(request)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        client_ip = rate_limiter._get_client_ip(request)
        minute_bucket = rate_limiter.minute_buckets.get(client_ip)
        
        if minute_bucket:
            response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(int(minute_bucket["tokens"]))
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
        
        return response
        
    except HTTPException as e:
        # Return rate limit error response
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail},
            headers=e.headers if hasattr(e, 'headers') else {}
        )