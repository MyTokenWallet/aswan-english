#!/usr/bin/env python3
# coding: utf-8

import logging
from risk_models.cache import menu_cache

logger = logging.getLogger(__name__)
logging.basicConfig()


def build_redis_key(event_code, dimension, menu_type):
    """
    :param event_code: List code
    :param dimension:  List dimensions
    :param menu_type:  ListType Black/White/Grey
    :return:
    """
    fields = ['menu', event_code, dimension, menu_type]
    if all(fields):
        return ':'.join(fields)
    else:
        return ''


def hit_menu(req_body, op_name, event, dimension, menu_type):
    if dimension not in req_body:
        logger.error('req_body(%s) does not contain %s', req_body, dimension)
        return False

    redis_key = build_redis_key(event, dimension, menu_type)

    if not redis_key:
        return False

    rv = req_body[dimension] in menu_cache[redis_key]
    if op_name == 'is_not':
        rv = not rv

    return rv
