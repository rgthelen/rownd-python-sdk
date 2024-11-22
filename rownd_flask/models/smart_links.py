from typing import Optional, Dict, Any
import requests
from ..exceptions import APIError, RowndError

class SmartLinkManager:
    def __init__(self, base_url, app_key, app_secret):
        self.base_url = base_url
        self.headers = {
            "x-rownd-app-key": app_key,
            "x-rownd-app-secret": app_secret,
            "Content-Type": "application/json"
        }

    async def create_magic_link(
        self,
        verification_type: str,
        data: Dict[str, Any],
        purpose: str = "auth",
        redirect_url: Optional[str] = None,
        user_id: Optional[str] = None,
        expiration: Optional[str] = None,
        group_to_join: Optional[str] = None
    ):
        """Create a magic link for authentication or verification"""
        url = f"{self.base_url}/hub/auth/magic"
        
        payload = {
            "purpose": purpose,
            "verification_type": verification_type,
            "data": data
        }

        # Add optional parameters if provided
        if redirect_url:
            payload["redirect_url"] = redirect_url
        if user_id:
            payload["user_id"] = user_id
        if expiration:
            payload["expiration"] = expiration
        if group_to_join:
            payload["group_to_join"] = group_to_join

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            
            if response.status_code != 200:
                raise APIError(f"Failed to create magic link: {response.text}")
                
            return response.json()
            
        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
