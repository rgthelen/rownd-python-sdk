import pytest
from urllib.parse import urlparse
from rownd_flask import RowndClient
from rownd_flask.models.auth import TokenValidationResponse
from rownd_flask.exceptions import AuthenticationError
from .conftest import delete_test_user
import requests

# Constants from Go implementation
CLAIM_USER_ID = "https://auth.rownd.io/app_user_id"
CLAIM_IS_VERIFIED_USER = "https://auth.rownd.io/is_verified_user"
CLAIM_IS_ANONYMOUS = "https://auth.rownd.io/is_anonymous"
CLAIM_AUTH_LEVEL = "https://auth.rownd.io/auth_level"

# Test token with claims matching Go implementation
TEST_TOKEN = "eyJhbGciOiJFZERTQSIsImtpZCI6InNpZy0xNjQ0OTM3MzYwIn0.eyJqdGkiOiI0YWNmMWYyNS02ZDQ5LTQ4YTMtODU2NC00ZDBiYmE0YjU1MGUiLCJhdWQiOlsiYXBwOmFwcF94a2J1bWw0OHFzM3R5eHhqanBheGVlbXYiXSwic3ViIjoidXNlcl9keXJtbHUwNGUyMnEwOHRieThvb3NkaDUiLCJpYXQiOjE3MzIxNzExNDcsImh0dHBzOi8vYXV0aC5yb3duZC5pby9hcHBfdXNlcl9pZCI6InVzZXJfZHlybWx1MDRlMjJxMDh0Ynk4b29zZGg1IiwiaHR0cHM6Ly9hdXRoLnJvd25kLmlvL2lzX3ZlcmlmaWVkX3VzZXIiOnRydWUsImh0dHBzOi8vYXV0aC5yb3duZC5pby9pc19hbm9ueW1vdXMiOnRydWUsImh0dHBzOi8vYXV0aC5yb3duZC5pby9hdXRoX2xldmVsIjoiZ3Vlc3QiLCJpc3MiOiJodHRwczovL2FwaS5yb3duZC5pbyIsImV4cCI6MTczMjE3NDc0N30.jQUMjc9EyRCqCKAQh61wi3OuGRZAPlcabP7w6FOJb7wqYFUFSuA5-BPltpgorY99h_F8wIVF-WXORAyAve8cCA"

# Token with expired timestamp
EXPIRED_TOKEN = "eyJhbGciOiJFZERTQSIsImtpZCI6InNpZy0xNjQ0OTM3MzYwIn0.eyJqdGkiOiIxOGIyZDU4MS1jNWJhLTQ3NzUtOGFjYS1hNWJmYTgwOGVkNmYiLCJhdWQiOlsiYXBwOmFwcF94a2J1bWw0OHFzM3R5eHhqanBheGVlbXYiXSwic3ViIjoidXNlcl9iZXA5OTM0MTJvajdiM2JiZnFpYTcyajciLCJpYXQiOjE3MzIxNDg4MzQsImh0dHBzOi8vYXV0aC5yb3duZC5pby9hcHBfdXNlcl9pZCI6InVzZXJfYmVwOTkzNDEyb2o3YjNiYmZxaWE3Mmo3IiwiaHR0cHM6Ly9hdXRoLnJvd25kLmlvL2lzX3ZlcmlmaWVkX3VzZXIiOnRydWUsImh0dHBzOi8vYXV0aC5yb3duZC5pby9pc19hbm9ueW1vdXMiOnRydWUsImh0dHBzOi8vYXV0aC5yb3duZC5pby9hdXRoX2xldmVsIjoiZ3Vlc3QiLCJpc3MiOiJodHRwczovL2FwaS5yb3duZC5pbyIsImV4cCI6MTczMjE1MjQzNH0.YK9npT3jNSWEvR4BosdsrPcJgCDHwxu3D_PRYSKz6LrCT9BOeLC9CLGV_dhFDyEeLlushY5qr2Oxw8FIlS40BQ"

# Token with wrong audience
INVALID_AUDIENCE_TOKEN = "eyJhbGciOiJFZERTQSIsImtpZCI6InNpZy0xNjQ0OTM3MzYwIn0.eyJqdGkiOiI1OGE1NGU2NC03ZjlmLTQ3YWItOWM1ZS1jYTI4ZjQ5MGFiNzMiLCJhdWQiOlsiYXBwOmNtMmI0dHRzOTAwY3Nuem15bnNrNmw4Y2YiXSwic3ViIjoidXNlcl9mdmF2bDI4NmJ0Nnl6eXN0bXo0OTJxNjAiLCJpYXQiOjE3MjkxMDg3NDQsImh0dHBzOi8vYXV0aC5yb3duZC5pby9hcHBfdXNlcl9pZCI6InVzZXJfZnZhdmwyODZidDZ5enlzdG16NDkycTYwIiwiaHR0cHM6Ly9hdXRoLnJvd25kLmlvL2lzX3ZlcmlmaWVkX3VzZXIiOnRydWUsImh0dHBzOi8vYXV0aC5yb3duZC5pby9hdXRoX2xldmVsIjoiaW5zdGFudCIsImlzcyI6Imh0dHBzOi8vYXBpLnJvd25kLmlvIiwiZXhwIjoxNzI5MTEyMzQ0fQ.ob4QX_gJvVJZsUWxB3Ap8mWbJYagnFiS0YRzl_gjguzH1Nu92YEnuDgwQi6Sl96VBgX_CZb8x3gh0M2Ekmr-AQ"

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_invalid_token(client):
    """Test validation with invalid token"""
    with pytest.raises(AuthenticationError) as exc_info:
        await client.auth.validate_token("invalid_token")
    assert str(exc_info.value) == "Invalid token format"

@pytest.mark.asyncio
async def test_expired_token(client):
    """Test validation with expired token"""
    with pytest.raises(AuthenticationError) as exc_info:
        await client.auth.validate_token(EXPIRED_TOKEN)
    assert str(exc_info.value) == "Token has expired"

@pytest.mark.asyncio
async def test_invalid_audience(client):
    """Test validation with invalid audience"""
    with pytest.raises(AuthenticationError) as exc_info:
        await client.auth.validate_token(INVALID_AUDIENCE_TOKEN)
    assert str(exc_info.value) == "Invalid audience"

@pytest.mark.asyncio
async def test_valid_token_flow(client):
    """Test full flow: create magic link -> redeem it -> validate token"""
    app_user_id = None
    try:
        # Create magic link
        link_response = await client.smart_links.create_magic_link(
            verification_type="email",
            data={
                "email": "testlink@example.com",
                "first_name": "Test"
            },
            purpose="auth",
            redirect_url="https://example.com/redirect",
            expiration="30d"
        )
        
        assert link_response is not None
        assert "link" in link_response
        
        # Extract link ID from URL
        url_parts = urlparse(link_response["link"])
        link_id = url_parts.path.split('/')[-1]
        
        # Create redemption URL and headers
        redemption_url = f"{client.base_url}/hub/auth/magic/{link_id}"
        headers = {"User-Agent": "rownd sdk"}
        
        # Make redemption request using requests directly
        response = requests.get(redemption_url, headers=headers)
        response_data = response.json()
        
        assert "access_token" in response_data
        valid_token = response_data["access_token"]
        app_user_id = response_data.get("app_user_id")
        
        # Validate the token
        validation = await client.auth.validate_token(valid_token)
        assert validation is not None
        assert validation.decoded_token is not None
        
    except Exception as e:
        pytest.fail(f"Token flow failed: {str(e)}")
    finally:
        if app_user_id:
            await delete_test_user(client, app_user_id)

@pytest.mark.asyncio
async def test_invalid_token(client):
    """Test validation with invalid token"""
    with pytest.raises(AuthenticationError) as exc_info:
        await client.auth.validate_token("invalid_token")
    assert str(exc_info.value) == "Invalid token format"

@pytest.mark.asyncio
async def test_expired_token(client):
    """Test validation with expired token"""
    with pytest.raises(AuthenticationError) as exc_info:
        await client.auth.validate_token(EXPIRED_TOKEN)
    assert str(exc_info.value) == "Token has expired"

@pytest.mark.asyncio
async def test_invalid_audience(client):
    """Test validation with invalid audience"""
    with pytest.raises(AuthenticationError) as exc_info:
        await client.auth.validate_token(INVALID_AUDIENCE_TOKEN)
    assert str(exc_info.value) == "Invalid audience"
