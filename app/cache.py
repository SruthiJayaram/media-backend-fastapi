"""
Redis caching service for analytics data
Task 3: Performance optimization
"""

import json
import redis
from typing import Optional, Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connect()

    def _connect(self):
        """Connect to Redis with fallback for development"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis connected successfully")
        except (redis.RedisError, ConnectionError) as e:
            logger.warning(f"⚠️  Redis connection failed: {e}. Falling back to no-cache mode.")
            self.redis_client = None

    def get_analytics(self, media_id: int) -> Optional[Dict[str, Any]]:
        """Get cached analytics data for media"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"analytics:media:{media_id}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"📊 Cache HIT for media {media_id}")
                return json.loads(cached_data)
            
            logger.info(f"📊 Cache MISS for media {media_id}")
            return None
            
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set_analytics(self, media_id: int, analytics_data: Dict[str, Any]) -> bool:
        """Cache analytics data for media"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = f"analytics:media:{media_id}"
            serialized_data = json.dumps(analytics_data, default=str)  # Handle datetime serialization
            
            self.redis_client.setex(
                cache_key, 
                settings.CACHE_TTL, 
                serialized_data
            )
            
            logger.info(f"📊 Cached analytics for media {media_id} (TTL: {settings.CACHE_TTL}s)")
            return True
            
        except (redis.RedisError, json.JSONEncodeError) as e:
            logger.error(f"Cache set error: {e}")
            return False

    def invalidate_analytics(self, media_id: int) -> bool:
        """Invalidate cached analytics when new views are added"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = f"analytics:media:{media_id}"
            deleted = self.redis_client.delete(cache_key)
            
            if deleted:
                logger.info(f"🗑️  Invalidated cache for media {media_id}")
            
            return bool(deleted)
            
        except redis.RedisError as e:
            logger.error(f"Cache invalidation error: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Check Redis health status"""
        if not self.redis_client:
            return {
                "status": "disabled",
                "message": "Redis not available - running without cache"
            }
        
        try:
            self.redis_client.ping()
            return {
                "status": "healthy",
                "message": "Redis connection active"
            }
        except redis.RedisError as e:
            return {
                "status": "error", 
                "message": f"Redis error: {e}"
            }

# Global cache instance
cache_service = CacheService()
