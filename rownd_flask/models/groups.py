from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import aiohttp
import logging
from ..exceptions import APIError
import json

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class GroupInvite:
    id: str
    group_id: str
    email: str
    status: str
    expires_at: Optional[str] = None

@dataclass
class Group:
    id: str
    name: str
    description: Optional[str] = None
    members: Optional[List[Dict[str, Any]]] = None
    invites: Optional[List[GroupInvite]] = None

@dataclass
class GroupMember:
    id: str
    user_id: str
    roles: List[str]
    state: str
    profile: Optional[Dict[str, Any]] = None

class GroupManager:
    def __init__(self, base_url, app_key, app_secret):
        self.base_url = base_url
        self.headers = {
            "x-rownd-app-key": app_key,
            "x-rownd-app-secret": app_secret,
            "Content-Type": "application/json"
        }
        self._session = None

    async def _get_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session

    async def _handle_response_error(self, response):
        """Handle API error responses with detailed logging"""
        try:
            error_text = await response.text()
            logger.debug(f"Raw error response: {error_text}")
            
            try:
                error_data = await response.json()
                error_message = error_data.get('message', error_text)
                error_code = error_data.get('code', str(response.status))
                logger.error(f"Rownd API error: {response.status} - {error_code} - {error_message}")
                logger.debug(f"Full error response: {error_data}")
                raise APIError(f"Rownd API error ({response.status}): {error_message}")
            except ValueError:
                logger.error(f"Rownd API error: {response.status} - {error_text}")
                raise APIError(f"Rownd API error ({response.status}): {error_text}")
        except Exception as e:
            logger.error(f"Error handling API response: {e}")
            raise APIError(f"Failed to process API error response: {str(e)}")

    async def _make_request(self, method, url, json=None):
        """Make API request with error handling and logging"""
        session = await self._get_session()
        logger.debug(f"Making {method} request to {url}")
        if json:
            logger.debug(f"Request payload: {json}")
            
        try:
            async with session.request(method, url, json=json) as response:
                logger.debug(f"Response status: {response.status}")
                logger.debug(f"Response headers: {response.headers}")
                
                if not response.ok:
                    error_text = await response.text()
                    logger.debug(f"Error response body: {error_text}")
                    await self._handle_response_error(response)
                
                if response.status == 204:
                    return True
                    
                data = await response.json()
                logger.debug(f"Response data: {data}")
                return data
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise APIError(f"HTTP request failed: {str(e)}")

    async def create_group(self, app_id, name, admission_policy, meta=None):
        url = f"{self.base_url}/applications/{app_id}/groups"
        payload = {
            "name": name,
            "admission_policy": admission_policy,
            "meta": meta or {}
        }
        return await self._make_request("POST", url, json=payload)

    async def get_group(self, app_id, group_id):
        url = f"{self.base_url}/applications/{app_id}/groups/{group_id}"
        return await self._make_request("GET", url)

    async def list_groups(self, app_id):
        url = f"{self.base_url}/applications/{app_id}/groups"
        return await self._make_request("GET", url)

    async def update_group(self, app_id, group_id, name=None, admission_policy=None, meta=None):
        url = f"{self.base_url}/applications/{app_id}/groups/{group_id}"
        payload = {
            "name": name,
            "admission_policy": admission_policy,
            "meta": meta
        }
        return await self._make_request("PUT", url, json=payload)

    async def delete_group(self, app_id, group_id):
        url = f"{self.base_url}/applications/{app_id}/groups/{group_id}"
        return await self._make_request("DELETE", url)

    async def add_group_member(self, app_id, group_id, user_id, roles, state):
        url = f"{self.base_url}/applications/{app_id}/groups/{group_id}/members"
        payload = {
            "user_id": user_id,
            "roles": roles,
            "state": state
        }
        return await self._make_request("POST", url, json=payload)

    async def list_group_members(self, app_id, group_id):
        url = f"{self.base_url}/applications/{app_id}/groups/{group_id}/members"
        return await self._make_request("GET", url)

    async def update_group_member(self, app_id, group_id, member_id, user_id, roles, state):
        url = f"{self.base_url}/applications/{app_id}/groups/{group_id}/members/{member_id}"
        payload = {
            "user_id": user_id,
            "roles": roles,
            "state": state
        }
        return await self._make_request("PUT", url, json=payload)

    async def delete_group_member(self, app_id, group_id, member_id):
        url = f"{self.base_url}/applications/{app_id}/groups/{group_id}/members/{member_id}"
        return await self._make_request("DELETE", url)

    async def create_group_invite(self, app_id, group_id, user_id=None, email=None, phone=None, roles=None, redirect_url=None, app_variant_id=None):
        url = f"{self.base_url}/applications/{app_id}/groups/{group_id}/invites"
        
        # Build payload with exact order matching example
        payload = {}
        
        # Email first if provided
        if email:
            payload["email"] = email
        elif user_id:
            payload["user_id"] = user_id
        elif phone:
            payload["phone"] = phone
        else:
            raise APIError("One of email, user_id, or phone is required")

        # Roles second
        if not roles:
            raise APIError("roles is required")
        payload["roles"] = roles

        # Redirect URL third if provided
        if redirect_url:
            payload["redirect_url"] = redirect_url

        # Log the exact request being made
        print("\n=== Rownd Group Invite API Call ===")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps({k: '****' if 'secret' in k.lower() else v for k, v in self.headers.items()}, indent=2)}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print("===================================\n")

        try:
            response = await self._make_request("POST", url, json=payload)
            print(f"\nResponse: {json.dumps(response, indent=2)}\n")
            return response
        except Exception as e:
            logger.error(f"Failed to create group invite: {e}")
            raise
