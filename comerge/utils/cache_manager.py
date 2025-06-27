"""
缓存管理工具
负责缓存的抽象和统一管理
"""

import logging
from typing import Any, Optional, Callable
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, prefix: str = "ecommerce"):
        self.prefix = prefix
    
    def _make_key(self, key: str) -> str:
        """生成缓存键"""
        return f"{self.prefix}:{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            cache_key = self._make_key(key)
            return cache.get(cache_key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, timeout: int = 3600) -> bool:
        """设置缓存"""
        try:
            cache_key = self._make_key(key)
            cache.set(cache_key, value, timeout)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            cache_key = self._make_key(key)
            cache.delete(cache_key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def get_or_set(self, key: str, callback: Callable, timeout: int = 3600) -> Any:
        """获取缓存，不存在则调用回调函数设置"""
        try:
            cache_key = self._make_key(key)
            value = cache.get(cache_key)
            if value is None:
                value = callback()
                if value is not None:
                    cache.set(cache_key, value, timeout)
            return value
        except Exception as e:
            logger.error(f"Cache get_or_set error for key {key}: {e}")
            # 缓存失败时直接调用回调函数
            return callback()
    
    def delete_pattern(self, pattern: str):
        """删除匹配模式的缓存"""
        try:
            # 简化实现，删除常见的缓存键
            common_keys = [
                f"{pattern}:list",
                f"{pattern}:search",
                f"{pattern}:detail",
            ]
            for key in common_keys:
                self.delete(key)
        except Exception as e:
            logger.error(f"Cache delete_pattern error for pattern {pattern}: {e}")


# 全局缓存管理器实例
cache_manager = CacheManager()
