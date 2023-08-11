# flake8: noqa
from .settings import *

TEST_DATABASE_DICT = dj_database_url.parse(config("TEST_DATABASE_URL"))
DATABASES = {"default": TEST_DATABASE_DICT}
