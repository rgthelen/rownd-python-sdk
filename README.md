# Rownd Python SDK

The official Python SDK for Rownd, providing seamless authentication and user management integration for Flask applications.

## Installation

Install the package using pip:

```bash
pip install rownd-flask
```

## Quick Start

```python
from rownd_flask import RowndClient
Initialize the client
client = RowndClient(
app_key="your_app_key",
app_secret="your_app_secret",
app_id="your_app_id"
)
```

## Features

- User Authentication
- User Management
- Group Management
- Smart Links / Magic Links
- Async Support

## Authentication

```python
## Validate a token
validation = await client.auth.validate_token(token)
if validation.decoded_token:
user_id = validation.decoded_token.get('https://auth.rownd.io/app_user_id')

```
## User Management

```python
Create/Update a user
user = await client.users.update_user(
app_id="your_app_id",
user_id="", # Empty for new users
user_data={
"first_name": "John",
"last_name": "Doe",
"email": "john@example.com"
}
)
Get user details
user = await client.users.get_user(user_id)
Update specific field
await client.users.update_user_field(
app_id="your_app_id",
user_id="user_id",
field="first_name",
value="Jane"
)
```

## Group Management
```python
# Create a group
group = await client.groups.create_group(
app_id="your_app_id",
name="Test Group",
admission_policy="open"
)
#Update group
updated_group = await client.groups.update_group(
app_id="your_app_id",
group_id="group_id",
name="Updated Group Name"
)
```
### Adding Members
```python
# Add a user as a member with specific roles
member = await client.groups.add_group_member(
app_id="your_app_id",
group_id="group_id",
user_id="user_id",
roles=["member"],
state="active"
)
# Verify membership
members = await client.groups.list_group_members(app_id="your_app_id", group_id="group_id")
```
### Updating Member Roles
```python
# Update member roles and state
await client.groups.update_group_member(
app_id="your_app_id",
group_id="group_id",
member_id="member_id", # Obtained from add_group_member response
user_id="user_id",
roles=["member", "owner"],
state="active"
)
```
### Removing Members
```python
# Remove a member from the group
await client.groups.delete_group_member(
app_id="your_app_id",
group_id="group_id",
member_id="member_id" # Obtained from add_group_member response
)
```
### Creating Group Invites
```python
# Create an invite by email
invite = await client.groups.create_group_invite(
app_id="your_app_id",
group_id="group_id",
email="new.member@example.com",
roles=["member"],
redirect_url="/welcome" # Optional
)
## The invite response contains:
## - link: The invitation link to send to the user
## - user_id: The ID of the invited user
```

## Smart Links

```python
# Create a magic link
link = await client.smart_links.create_magic_link(
verification_type="email",
data={
"email": "user@example.com",
"first_name": "Test"
},
redirect_url="/dashboard",
expiration="30d"
)
```
## Async Context Manager Support
```python
async with RowndClient(app_key="key", app_secret="secret") as client:
user = await client.users.get_user("user_id")
```

## Error Handling
```python
from rownd_flask.exceptions import AuthenticationError, APIError
try:
await client.auth.validate_token(token)
except AuthenticationError as e:
print(f"Authentication failed: {e}")
except APIError as e:
print(f"API error: {e}")
```

## Development

1. Clone the repository
2. Install dependencies:

```bash
pip install -e ".[dev]"
```

3. Run tests:

```bash
pytest
```
OR
```bash
python -m pytest tests
```

## Development Setup (to run the tests)

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Update the `.env` file with your Rownd credentials:

```bash
ROWND_APP_KEY=your_app_key_here
ROWND_APP_SECRET=your_app_secret_here
ROWND_APP_ID=your_app_id_here

```

## Reference Documentation

For detailed API documentation and examples, visit [Rownd's documentation](https://docs.rownd.io).

## License

MIT License - see LICENSE file for details.

## Support

For support, please contact support@rownd.io.