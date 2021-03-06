# coding: utf-8
"""Production environment configuration"""

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
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
