__title__ = "pastey.gg"
__author__ = "PythonistaGuild"
__license__ = "MIT"
__copyright__ = "Copyright 2026-present PythonistaGuild"
__version__ = "0.0.1a"

import logging

from .client import Client as Client, SyncClient as SyncClient
from .file import *
from .paste import *

logging.getLogger(__name__).addHandler(logging.NullHandler())  # noqa: RUF067 # setup base logger
