import os

# Settings are read at import time, so the required ones must be set first.
os.environ.setdefault("PG_HOST", "localhost")
os.environ.setdefault("PG_USER", "postgres")
os.environ.setdefault("FIRST_SUPERUSER_USERNAME", "admin")
os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "testsuperpassword")
