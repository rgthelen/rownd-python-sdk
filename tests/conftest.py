import pytest
import logging
import os
from dotenv import load_dotenv
from rownd_flask.client import RowndClient
from rownd_flask.models.smart_links import SmartLinkManager
from rownd_flask.exceptions import APIError

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Test constants from environment variables
TEST_APP_KEY = os.getenv('ROWND_APP_KEY')
TEST_APP_SECRET = os.getenv('ROWND_APP_SECRET')
TEST_APP_ID = os.getenv('ROWND_APP_ID')
TEST_BASE_URL = os.getenv('ROWND_BASE_URL', 'https://api.rownd.io')

@pytest.fixture
def client():
    """Create a client instance for tests"""
    return RowndClient(
        app_key=TEST_APP_KEY,
        app_secret=TEST_APP_SECRET,
        app_id=TEST_APP_ID,
        base_url=TEST_BASE_URL
    )

@pytest.fixture
def smart_link_manager():
    """Create a smart link manager instance for tests"""
    return SmartLinkManager(
        base_url="https://api.rownd.io",
        app_key=TEST_APP_KEY,
        app_secret=TEST_APP_SECRET
    )

async def delete_test_user(client, user_id):
    """Helper function to delete a test user"""
    try:
        await client.users.delete_user(
            app_id=TEST_APP_ID,
            user_id=user_id
        )
    except APIError:
        pass