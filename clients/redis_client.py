#!/usr/bin/env python3
# coding: utf-8

import redis
# for development import this:
# import config.develop as conf

# for production import this
import config.product as conf

from lru import lru_cache_function

__all__ = ['get_log_redis_client', 'get_config_redis_client', 'get_report_redis_client']


@lru_cache_function(max_size=1, expiration=24 * 3600)
def get_config_redis_client():
    return redis.StrictRedis(**conf.REDIS_CONFIG)


@lru_cache_function(max_size=1, expiration=24 * 3600)
def get_log_redis_client():
    return redis.StrictRedis(**conf.LOG_REDIS_CONFIG)


@lru_cache_function(max_size=1, expiration=24 * 3600)
def get_report_redis_client():
    return redis.StrictRedis(**conf.REPORT_REDIS_CONFIG)
