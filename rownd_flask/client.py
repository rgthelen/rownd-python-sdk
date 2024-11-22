from typing import Optional, Dict, Any
import aiohttp
import requests
from .models.auth import TokenValidationResponse, RowndAuth
from .models.users import RowndUsers
from .models.groups import GroupManager
from .models.smart_links import SmartLinkManager
from .exceptions import ConfigurationError, APIError

class RowndClient:
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        app_id: Optional[str] = None,
        base_url: str = "https://api.rownd.io",
    ):
        if not app_key or not app_secret:
            raise ConfigurationError("app_key and app_secret are required")
            
        self.app_key = app_key
        self.app_secret = app_secret
        self.app_id = app_id
        self.base_url = base_url
        
        # Initialize HTTP sessions
        self._session = requests.Session()
        self._async_session = None
        
        # Set default headers
        self._headers = {
            "x-rownd-app-key": app_key,
            "x-rownd-app-secret": app_secret,
            "Content-Type": "application/json",
        }
        self._session.headers.update(self._headers)
        
        # Initialize components
        self.auth = RowndAuth(self)
        self.users = RowndUsers(self)
        self.groups = GroupManager(base_url, app_key, app_secret)
        self.smart_links = SmartLinkManager(base_url, app_key, app_secret)

    async def __aenter__(self):
        self._async_session = aiohttp.ClientSession(headers=self._headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._async_session:
            await self._async_session.close()
