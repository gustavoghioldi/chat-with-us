"""Django settings initialization.

Import the appropriate settings based on the DJANGO_ENV environment variable.
"""

import os

ENV = os.environ.get("DJANGO_ENV", "development")

if ENV == "production":
    from .production import *  # noqa: F403, F401
else:
    from .development import *  # noqa: F403, F401
