import pytest
from rownd_flask.models.smart_links import SmartLinkManager
from rownd_flask.exceptions import APIError
from .conftest import delete_test_user, TEST_APP_KEY, TEST_APP_SECRET, TEST_APP_ID

pytestmark = pytest.mark.asyncio

async def test_create_magic_link(smart_link_manager, client):
    """Test creating a magic link"""
    app_user_id = None
    try:
        response = await smart_link_manager.create_magic_link(
            verification_type="email",
            data={
                "email": "test@example.com",
                "first_name": "Test"
            },
            redirect_url="/test/redirect",
            expiration="30d"
        )
        
        assert response is not None
        assert "link" in response
        assert response["link"].startswith("http")
        app_user_id = response.get('app_user_id')
        
    except APIError as e:
        pytest.fail(f"Failed to create magic link: {e}")
    finally:
        if app_user_id:
            await delete_test_user(client, app_user_id)
