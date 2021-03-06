# coding: utf-8
"""Test the configuration of the environment"""
# SECURITY WARNING: keep the secret key used in production secret!

DATABASES = {
    'default': {
        "ENGINE": 'django.db.backends.mysql',
        "HOST": "127.0.0.1",
        "PORT": 3306,
        "USER": "root",
        "PASSWORD": "root",
        "DATABASE_CHARSET": "utf8",
        "NAME": "risk_control",
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
}

DEBUG = True
