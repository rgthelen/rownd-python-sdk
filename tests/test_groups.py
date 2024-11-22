import pytest
import logging
from rownd_flask.client import RowndClient
from rownd_flask.models.groups import GroupManager
from rownd_flask.exceptions import APIError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # This will override any existing logging configuration
)
logger = logging.getLogger(__name__)

pytestmark = pytest.mark.asyncio

# Test constants
TEST_APP_KEY = "key_ckqzi463emvbamqhom5w6tbm"
TEST_APP_SECRET = "ras_fda63b246516781deaccada36eca7ee41f8c1e52bf23c932"
TEST_APP_ID = "app_xkbuml48qs3tyxxjjpaxeemv"

@pytest.fixture
def client():
    """Create a client instance for tests"""
    return RowndClient(
        app_key=TEST_APP_KEY,
        app_secret=TEST_APP_SECRET,
        app_id=TEST_APP_ID,
        base_url="https://api.rownd.io"
    )

@pytest.fixture
def group_manager(client):
    """Create a group manager instance for tests"""
    return client.groups

@pytest.fixture
def app_id():
    """Provide the application ID for tests"""
    return TEST_APP_ID

async def create_test_user(client, email):
    """Helper function to create a test user"""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": email
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

async def test_create_group(group_manager, app_id):
    """Test group creation and deletion"""
    try:
        # Create a group
        logger.info("Creating test group")
        group = await group_manager.create_group(app_id, "Test Group", "open")
        
        # Verify group
        assert group is not None
        assert group['name'] == "Test Group"
        assert group['admission_policy'] == "open"
        
    finally:
        # Cleanup
        if group:
            await group_manager.delete_group(app_id, group['id'])

async def test_edit_group(group_manager, app_id):
    """Test group editing"""
    group = None
    try:
        # Create initial group
        group = await group_manager.create_group(app_id, "Test Group", "open")
        
        # Edit group
        updated_group = await group_manager.update_group(
            app_id, 
            group['id'],
            name="Updated Group",
            admission_policy="invite_only"
        )
        
        # Verify changes
        assert updated_group['name'] == "Updated Group"
        assert updated_group['admission_policy'] == "invite_only"
        
    finally:
        if group:
            await group_manager.delete_group(app_id, group['id'])

async def test_add_member(group_manager, app_id, client):
    """Test adding a member to a group"""
    group = None
    user = None
    try:
        # Create group
        group = await group_manager.create_group(app_id, "Test Group", "open")
        
        # Create user
        user = await create_test_user(client, "add_member@example.com")
        
        # Add as member
        member = await group_manager.add_group_member(
            app_id, 
            group['id'], 
            user.id, 
            ["member"], 
            "active"
        )
        
        # Verify membership
        members = await group_manager.list_group_members(app_id, group['id'])
        assert len(members.get('results', [])) == 1
        assert members['results'][0]['user_id'] == user.id
        
    finally:
        if group:
            await group_manager.delete_group(app_id, group['id'])
        if user:
            await delete_test_user(client, user.id)


async def test_member_management(group_manager, app_id, client):
    """Test member role changes and deletion"""
    group = None
    owner = None
    member = None
    try:
        # Create group and users
        group = await group_manager.create_group(app_id, "Test Group", "open")
        owner = await create_test_user(client, "member_management_owner@example.com")
        member = await create_test_user(client, "member_management_member@example.com")
        
        # Add both users and store their member responses
        owner_member = await group_manager.add_group_member(
            app_id, group['id'], owner.id, ["member", "owner"], "active"
        )
        regular_member = await group_manager.add_group_member(
            app_id, group['id'], member.id, ["member"], "active"
        )
        
        # Store the member_id from the add response
        member_id = regular_member['id']
        
        # Verify initial roles
        members = await group_manager.list_group_members(app_id, group['id'])
        assert len(members.get('results', [])) == 2
        
        # Update member roles using member_id and user_id
        await group_manager.update_group_member(
            app_id, 
            group['id'], 
            member_id,  # member_id from add response
            member.id,  # user_id still needed in payload
            ["member", "owner"], 
            "active"
        )
        
        # Delete member using member_id
        await group_manager.delete_group_member(
            app_id, 
            group['id'], 
            member_id  # Use member_id from add response
        )
        
        # Verify final state
        final_members = await group_manager.list_group_members(app_id, group['id'])
        assert len(final_members.get('results', [])) == 1
        
    finally:
        if member:
            await delete_test_user(client, member.id)
        if group:
            await group_manager.delete_group(app_id, group['id'])
        if owner:
            await delete_test_user(client, owner.id)


async def test_create_group_invite(group_manager, app_id, client):
    """Test creating a group invite"""
    owner = None
    group = None
    invited_user_id = None
    
    try:
        # Create a group
        logger.info("Creating test group")
        group = await group_manager.create_group(app_id, "Test Group", "open")
        assert group is not None
        logger.debug(f"Created group: {group}")

        # Create invite
        logger.info("Creating group invite")
        invite = await group_manager.create_group_invite(
            app_id,
            group['id'],
            email="invite2@example.com",
            roles=["member"]
        )
        logger.debug(f"Created invite: {invite}")
        
        # Verify invite
        assert invite is not None
        assert 'link' in invite, "Invite response should contain a link"
        assert isinstance(invite['link'], str), "Invite link should be a string"
        assert invite['link'].startswith('http'), "Invite link should be a valid URL"
        
        # Store invited user ID
        invited_user_id = invite.get('user_id')
        assert invited_user_id is not None, "Invite response should contain a user_id"
        
    except APIError as e:
        logger.error(f"API Error during test: {e}")
        raise
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise
    finally:
        # Cleanup in reverse order of creation
        logger.info("Cleaning up test resources")
        if invited_user_id:
            await delete_test_user(client, invited_user_id)
        if group:
            await group_manager.delete_group(app_id, group['id'])
