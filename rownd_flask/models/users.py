from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
from ..exceptions import RowndError, APIError
import requests

@dataclass
class User:
    id: str
    data: Dict[str, Any]
    auth_level: Optional[str] = None
    state: Optional[str] = None
    verified_data: Optional[Dict[str, Any]] = None
    groups: Optional[list] = None
    meta: Optional[Dict[str, Any]] = None
    connection_map: Optional[Dict[str, Any]] = None
    rownd_user: Optional[str] = None
    
    def __init__(self, id: str, **kwargs):
        self.id = id
        # Set known fields
        self.data = kwargs.get('data', {})
        self.auth_level = kwargs.get('auth_level')
        self.state = kwargs.get('state')
        self.verified_data = kwargs.get('verified_data')
        self.groups = kwargs.get('groups', [])
        self.meta = kwargs.get('meta', {})
        self.connection_map = kwargs.get('connection_map', {})
        self.rownd_user = kwargs.get('rownd_user')
        
        # Store any additional fields that might be added in the future
        self._additional_fields = {
            k: v for k, v in kwargs.items() 
            if k not in ['data', 'auth_level', 'state', 'verified_data', 
                        'groups', 'meta', 'connection_map', 'rownd_user']
        }

class RowndUsers:
    def __init__(self, client):
        self.client = client
        
    async def get_user(self, user_id: str, token_info: Optional[Dict[str, Any]] = None) -> User:
        """Get user details by ID"""
        # Get app ID from token claims
        app_id = ""
        if token_info and token_info.decoded_token:
            aud = token_info.decoded_token.get("aud")
            if isinstance(aud, list) and len(aud) > 0:
                if aud[0].startswith("app:"):
                    app_id = aud[0][4:]
            elif isinstance(aud, str) and aud.startswith("app:"):
                app_id = aud[4:]

        # If no app ID in token, use the one from client config
        if not app_id:
            app_id = self.client.app_id

        if not app_id:
            raise RowndError("app ID not found in token or client config")

        url = f"{self.client.base_url}/applications/{app_id}/users/{user_id}/data"
        headers = {
            "x-rownd-app-key": self.client.app_key,
            "x-rownd-app-secret": self.client.app_secret,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code == 404:
            raise APIError(f"API error: User not found (404)")
        elif response.status_code != 200:
            raise APIError(f"API error: {response.text}")

        user_data = response.json()
        return User(id=user_id, **user_data)

    async def update_user(self, app_id: str, user_id: str, user_data: Dict[str, Any]) -> User:
        """Update or create user"""
        if not app_id:
            raise RowndError("app ID is required")

        # Only use __UUID__ for empty user_id
        is_new_user = user_id == ""
        if is_new_user:
            user_id = "__UUID__"

        url = f"{self.client.base_url}/applications/{app_id}/users/{user_id}/data"
        payload = {"data": user_data}
        
        headers = {
            "x-rownd-app-key": self.client.app_key,
            "x-rownd-app-secret": self.client.app_secret,
            "Content-Type": "application/json"
        }

        response = requests.put(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise APIError(f"API error: {response.text}")

        response_data = response.json()
        
        if is_new_user:
            # Extract user ID from the data object
            user_id = response_data.get('data', {}).get('user_id')
            if not user_id:
                raise APIError(f"No user ID returned for new user. Response: {response_data}")

        return User(id=user_id, **response_data)

    async def patch_user(self, app_id: str, user_id: str, data: Dict[str, Any]) -> User:
        """Partially update user data"""
        if not app_id:
            raise RowndError("app ID is required")
        if not user_id:
            raise RowndError("user ID is required")

        url = f"{self.client.base_url}/applications/{app_id}/users/{user_id}/data"
        payload = {"data": data}
        
        headers = {
            "x-rownd-app-key": self.client.app_key,
            "x-rownd-app-secret": self.client.app_secret,
            "Content-Type": "application/json"
        }

        response = requests.patch(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise APIError(f"API error: {response.text}")

        user_data = response.json()
        return User(id=user_id, **user_data)

    async def get_user_field(self, app_id: str, user_id: str, field: str) -> Any:
        """Get a specific user field"""
        if not app_id:
            raise RowndError("app ID is required")
        if not user_id:
            raise RowndError("user ID is required")

        # Instead of using the fields endpoint, get the full user and extract the field
        url = f"{self.client.base_url}/applications/{app_id}/users/{user_id}/data"
        
        headers = {
            "x-rownd-app-key": self.client.app_key,
            "x-rownd-app-secret": self.client.app_secret,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise APIError(f"API error: {response.text}")

        user_data = response.json()
        return user_data.get('data', {}).get(field)

    async def update_user_field(self, app_id: str, user_id: str, field: str, value: Any) -> None:
        """Update a specific user field"""
        if not app_id:
            raise RowndError("app ID is required")
        if not user_id:
            raise RowndError("user ID is required")

        url = f"{self.client.base_url}/applications/{app_id}/users/{user_id}/data/fields/{field}"
        payload = {"value": value}
        
        headers = {
            "x-rownd-app-key": self.client.app_key,
            "x-rownd-app-secret": self.client.app_secret,
            "Content-Type": "application/json"
        }

        response = requests.put(url, headers=headers, json=payload)
        
        if response.status_code not in (200, 204):
            raise APIError(f"API error: {response.text}")

    async def delete_user(self, app_id: str, user_id: str) -> None:
        """Delete a user"""
        if not app_id:
            raise RowndError("app ID is required")
        if not user_id:
            raise RowndError("user ID is required")

        url = f"{self.client.base_url}/applications/{app_id}/users/{user_id}/data"
        
        headers = {
            "x-rownd-app-key": self.client.app_key,
            "x-rownd-app-secret": self.client.app_secret,
        }

        response = requests.delete(url, headers=headers)
        
        if response.status_code not in [200, 204]:
            raise APIError(f"API error: {response.text}")
