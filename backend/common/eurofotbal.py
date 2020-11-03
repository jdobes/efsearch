from common.config import EF_USER, EF_PASSWORD, EF_LOGIN_URL
from common.logging import get_logger

LOGGER = get_logger(__name__)


async def login(session):
    payload = {'login': EF_USER, 'pass': EF_PASSWORD}
    async with session.post(EF_LOGIN_URL, data=payload) as response:
        LOGGER.info(f"Login as {EF_USER}:{EF_PASSWORD} - HTTP {response.status}")
