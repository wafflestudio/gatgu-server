from django.core.cache import cache


def cache_test():
    cache.set("testkey", "testvalue", timeout=10)
    cache.get("testkey")
