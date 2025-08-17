"""
Rate limiting service for API endpoints
Task 3: Security and abuse prevention
"""

import time
from typing import Dict, Tuple
from collections import defaultdict, deque
from fastapi import HTTPException, Request
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        # In-memory storage for rate limiting (in production, use Redis)
        self._requests: Dict[str, deque] = defaultdict(deque)
        self._window_size = 60  # 1 minute window
        
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Try to get real IP if behind proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, requests_deque: deque, current_time: float):
        """Remove requests outside the time window"""
        while requests_deque and current_time - requests_deque[0] > self._window_size:
            requests_deque.popleft()
    
    def check_rate_limit(self, request: Request) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request is within rate limit
        Returns (allowed, rate_limit_info)
        """
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Get client's request history
        client_requests = self._requests[client_id]
        
        # Clean up old requests
        self._cleanup_old_requests(client_requests, current_time)
        
        # Check if within limit
        current_count = len(client_requests)
        limit = settings.RATE_LIMIT_PER_MINUTE
        
        rate_limit_info = {
            "limit": limit,
            "remaining": max(0, limit - current_count),
            "reset_at": int(current_time + self._window_size),
            "current_count": current_count
        }
        
        if current_count >= limit:
            logger.warning(f"🚫 Rate limit exceeded for {client_id}: {current_count}/{limit}")
            return False, rate_limit_info
        
        # Add current request
        client_requests.append(current_time)
        rate_limit_info["remaining"] -= 1
        rate_limit_info["current_count"] += 1
        
        logger.debug(f"✅ Rate limit OK for {client_id}: {rate_limit_info['current_count']}/{limit}")
        return True, rate_limit_info
    
    def enforce_rate_limit(self, request: Request):
        """
        Enforce rate limit, raise HTTPException if exceeded
        """
        allowed, rate_info = self.check_rate_limit(request)
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Rate limit exceeded. Too many requests.",
                    "limit": rate_info["limit"],
                    "reset_at": rate_info["reset_at"],
                    "retry_after": 60
                }
            )
        
        return rate_info

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit_dependency(request: Request):
    """FastAPI dependency for rate limiting"""
    return rate_limiter.enforce_rate_limit(request)
