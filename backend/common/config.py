import os

NATS_HOST = os.getenv("NATS_HOST", "nats://efs-nats:4222")
NATS_PAGES_TOPIC = os.getenv("NATS_PAGES_TOPIC", "sync_pages")

POSTGRES_USER = os.getenv("POSTGRES_USER", "unknown")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "unknown")
POSTGRES_DB = os.getenv("POSTGRES_DB", "unknown")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "unknown")

FETCHER_TASKS = int(os.getenv("FETCHER_TASKS", "16"))

EF_USER = os.getenv("EF_USER", "")
EF_PASSWORD = os.getenv("EF_PASSWORD", "")
EF_BASE_URL = os.getenv("EF_BASE_URL", "https://www.eurofotbal.cz")
EF_LOGIN_PATH = os.getenv("EF_LOGIN_PATH", "/muj/login/")
EF_UPDATES_PATH = os.getenv("EF_UPDATES_PATH", "/res/ajax/myefBox.php")

EF_LOGIN_URL = f"{EF_BASE_URL}{EF_LOGIN_PATH}"
EF_UPDATES_URL = f"{EF_BASE_URL}{EF_UPDATES_PATH}"

QUEUE_NEW_PAGES_INTERVAL = int(os.getenv("QUEUE_NEW_PAGES_INTERVAL", "14400"))  # 4 hours
REFRESH_POST_CACHE_INTERVAL = int(os.getenv("REFRESH_POST_CACHE_INTERVAL", "600"))  # 10 mins
