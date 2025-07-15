"""
Django settings for CI/CD pipeline.

This file is used specifically for running collectstatic during CI/CD pipeline.
It uses minimal configuration to avoid dependencies.
"""

from pathlib import Path
import os
from .base import *

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Disable logging to avoid noise in CI/CD pipeline
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}
