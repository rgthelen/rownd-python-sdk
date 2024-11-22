from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
import json
from base64 import b64decode, urlsafe_b64decode
import time
from jwt import decode, get_unverified_header, InvalidTokenError, ExpiredSignatureError, InvalidSignatureError, InvalidAudienceError
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from ..exceptions import RowndError, AuthenticationError, APIError
from .models import TokenValidationResponse, JWKS, WellKnownConfig
import requests

# Auth level constants
AUTH_LEVEL_INSTANT = "instant"
AUTH_LEVEL_UNVERIFIED = "unverified"
AUTH_LEVEL_GUEST = "guest"
AUTH_LEVEL_VERIFIED = "verified"

# Claim constants
CLAIM_USER_ID = "https://auth.rownd.io/app_user_id"
CLAIM_IS_VERIFIED_USER = "https://auth.rownd.io/is_verified_user"
CLAIM_IS_ANONYMOUS = "https://auth.rownd.io/is_anonymous"
CLAIM_AUTH_LEVEL = "https://auth.rownd.io/auth_level"

@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str

@dataclass
class AuthInitRequest:
    email: str
    return_url: str
    continue_with_email: bool = False
    fingerprint: Optional[Dict[str, Any]] = None

@dataclass
class AuthInitResponse:
    challenge_id: str
    challenge_token: str
    auth_tokens: Optional[AuthTokens] = None

@dataclass
class AuthCompleteRequest:
    token: str
    challenge_id: str
    email: str

@dataclass
class AuthCompleteResponse:
    redirect_url: str

@dataclass
class TokenValidationResponse:
    decoded_token: Dict[str, Any]
    access_token: str

@dataclass
class MagicLinkResponse:
    access_token: str
    refresh_token: str
    app_user_id: str
    app_id: str
    last_sign_in: str
    redirect_url: str

@dataclass
class JWKS:
    keys: list[Dict[str, Any]]

class RowndAuth:
    def __init__(self, client):
        self.app_key = client.app_key
        self.app_secret = client.app_secret
        self.app_id = client.app_id
        self.base_url = client.base_url
        self._jwks_cache = None
        self._jwks_cache_time = None
        self._config_cache = None
        self._config_cache_time = None
        self.client = client

    async def validate_token(self, token: str) -> TokenValidationResponse:
        try:
            config = await self._get_well_known_config()
            jwks = await self._get_jwks(config.jwks_uri)
            
            # Get unverified headers to find key ID
            try:
                headers = get_unverified_header(token)
            except Exception as e:
                raise AuthenticationError("Invalid token format")

            if 'kid' not in headers:
                raise AuthenticationError("No 'kid' in token headers")

            # Find matching key
            key_data = None
            for jwk_key in jwks.keys:
                if jwk_key.get('kid') == headers['kid']:
                    key_data = jwk_key
                    break

            if not key_data:
                raise AuthenticationError(f"No matching key found for kid: {headers['kid']}")

            # Convert JWK to public key
            try:
                padded_x = key_data['x'] + '=' * (-len(key_data['x']) % 4)
                x = urlsafe_b64decode(padded_x.encode('utf-8'))
                public_key = Ed25519PublicKey.from_public_bytes(x)
            except Exception as e:
                raise AuthenticationError("Invalid key format")

            try:
                # Verify and decode token
                decoded_token = decode(
                    token,
                    key=public_key,
                    algorithms=['EdDSA'],
                    options={
                        'verify_aud': True,
                        'verify_exp': False,  # Temporarily disable other validations
                        'verify_iat': False,
                        'verify_iss': False,
                        'require_exp': False,
                        'require_iat': False,
                    },
                    audience=f"app:{self.app_id}"
                )

                # Now check expiration and other claims
                decoded_token = decode(
                    token,
                    key=public_key,
                    algorithms=['EdDSA'],
                    options={
                        'verify_aud': False,  # Already validated
                        'verify_exp': True,
                        'verify_iat': True,
                        'verify_iss': True,
                        'require_exp': True,
                        'require_iat': True,
                    }
                )
            except InvalidAudienceError:
                raise AuthenticationError("Invalid audience")
            except ExpiredSignatureError:
                raise AuthenticationError("Token has expired")
            except Exception as e:
                raise AuthenticationError(f"Token validation failed: {str(e)}")

            return TokenValidationResponse(
                decoded_token=decoded_token,
                access_token=token
            )

        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"Unexpected error: {str(e)}")

    async def _get_well_known_config(self) -> WellKnownConfig:
        """Internal method to fetch and cache well-known config"""
        if (self._config_cache and self._config_cache_time and 
            (time.time() - self._config_cache_time) < 3600):
            return self._config_cache

        url = f"{self.base_url}/hub/auth/.well-known/oauth-authorization-server"
        response = requests.get(url)
        if response.status_code != 200:
            raise APIError("Failed to fetch well-known config")

        config_data = response.json()
        self._config_cache = WellKnownConfig(**config_data)
        self._config_cache_time = time.time()
        return self._config_cache

    async def _get_jwks(self, jwks_uri: str) -> JWKS:
        """Internal method to fetch and cache JWKS"""
        if (self._jwks_cache and self._jwks_cache_time and 
            (time.time() - self._jwks_cache_time) < 3600):
            return self._jwks_cache

        response = requests.get(jwks_uri)
        if response.status_code != 200:
            raise APIError("Failed to fetch JWKS")

        jwks_data = response.json()
        self._jwks_cache = JWKS(**jwks_data)
        self._jwks_cache_time = time.time()
        return self._jwks_cache

    def _decode_ed25519_public_key(self, x: str) -> bytes:
        """Decode EdDSA public key from base64url format"""
        try:
            return base64.urlsafe_b64decode(x + '=' * (-len(x) % 4))
        except Exception as e:
            raise AuthenticationError(f"Failed to decode public key: {str(e)}")

    async def _make_request(self, method: str, url: str, headers: dict = None) -> dict:
        """Make HTTP request with proper error handling"""
        try:
            response = requests.request(
                method,
                url,
                headers=headers
            )
            
            if response.status_code != 200:
                raise APIError(f"Request failed: {response.text}")
                
            return response.json()
            
        except requests.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
