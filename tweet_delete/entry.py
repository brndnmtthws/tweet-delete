from gevent import monkey

monkey.patch_all()

# Do not reorder imports
from .main import *  # NOQA: E402
