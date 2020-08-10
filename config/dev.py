"""

AUTOR: jarquinsandra


"""
# config/dev.py
from .default import *

APP_ENV = APP_ENV_DEVELOPMENT

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:8889/Forest_python'
SQLALCHEMY_ECHO = True