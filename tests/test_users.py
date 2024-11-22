import pytest
from rownd_flask.client import RowndClient
from rownd_flask.exceptions import APIError
from .conftest import TEST_APP_ID, TEST_APP_KEY, TEST_APP_SECRET

pytestmark = pytest.mark.asyncio

async def create_test_user(client):
    """Helper function to create a test user"""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com"
    }
    user = await client.users.update_user(
        app_id=TEST_APP_ID,
        user_id="",
        user_data=user_data
    )
    return user

async def delete_test_user(client, user_id):
    """Helper function to delete a test user"""
    try:
        await client.users.delete_user(
            app_id=TEST_APP_ID,
            user_id=user_id
        )
    except APIError:
        pass

async def test_create_user(client):
    """Test user creation"""
    user = await create_test_user(client)
    
    assert user is not None
    assert user.id != ""
    assert user.data.get("first_name") == "Test"
    assert user.data.get("last_name") == "User"
    assert user.data.get("email") == "test@example.com"

    # Cleanup
    await delete_test_user(client, user.id)

async def test_get_user(client):
    """Test fetching a user"""
    user = await create_test_user(client)
    fetched_user = await client.users.get_user(user.id)
    
    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert fetched_user.data.get("first_name") == "Test"

    # Cleanup
    await delete_test_user(client, user.id)

async def test_update_user_field(client):
    """Test updating a specific user field"""
    user = await create_test_user(client)
    
    await client.users.update_user_field(
        app_id=TEST_APP_ID,
        user_id=user.id,
        field="first_name",
        value="Updated"
    )
    
    updated_user = await client.users.get_user(user.id)
    assert updated_user.data.get("first_name") == "Updated"

    # Cleanup
    await delete_test_user(client, user.id)

async def test_get_user_field(client):
    """Test getting a specific user field"""
    user = await create_test_user(client)
    first_name = await client.users.get_user_field(
        app_id=TEST_APP_ID,
        user_id=user.id,
        field="first_name"
    )
    assert first_name == "Test"

    # Cleanup
    await delete_test_user(client, user.id)

async def test_patch_user(client):
    """Test patching user data"""
    user = await create_test_user(client)
    patch_data = {
        "last_name": "Developer"
    }
    patched_user = await client.users.patch_user(
        app_id=TEST_APP_ID,
        user_id=user.id,
        data=patch_data
    )
    
    assert patched_user is not None
    assert patched_user.id == user.id
    assert patched_user.data.get("last_name") == "Developer"

    # Cleanup
    await delete_test_user(client, user.id)

async def test_delete_user(client):
    """Test user deletion"""
    user = await create_test_user(client)
    
    # First delete the user
    await client.users.delete_user(
        app_id=TEST_APP_ID,
        user_id=user.id
    )
    
    # Then try to get the user - should raise APIError
    with pytest.raises(APIError) as exc_info:
        await client.users.get_user(user.id)
    assert "404" in str(exc_info.value)  # Verify it's a 404 error
