from flask import Flask, jsonify, request
from rownd_flask import RowndClient, require_auth
from rownd_flask.models.auth import TokenValidationResponse

app = Flask(__name__)

# Test JWT token (this is a sample EdDSA-signed token)
TEST_TOKEN = "eyJhbGciOiJFZERTQSIsImtpZCI6InNpZy0xNjQ0OTM3MzYwIn0.eyJqdGkiOiIwOTk3YmI3MC00MDY4LTRjMWItOGJjMS1lZjU2MjM5ODViNWIiLCJhdWQiOlsiYXBwOmFwcF94a2J1bWw0OHFzM3R5eHhqanBheGVlbXYiXSwic3ViIjoidXNlcl9xOTcxbm5kd3liano4enhnNjFqcTUzNmkiLCJpYXQiOjE3MzIxNjYyNzAsImh0dHBzOi8vYXV0aC5yb3duZC5pby9hcHBfdXNlcl9pZCI6InVzZXJfcTk3MW5uZHd5Ymp6OHp4ZzYxanE1MzZpIiwiaHR0cHM6Ly9hdXRoLnJvd25kLmlvL2lzX3ZlcmlmaWVkX3VzZXIiOnRydWUsImh0dHBzOi8vYXV0aC5yb3duZC5pby9hdXRoX2xldmVsIjoidmVyaWZpZWQiLCJpc3MiOiJodHRwczovL2FwaS5yb3duZC5pbyIsImV4cCI6MTczMjE2OTg3MH0.K1Bpf_JDs9ZeT6mMn2W2bCUt6yvq88wV7iCC2ykYbmnNtKv4jCZ4wYAMFLCpWHIxSiEvwQKhJ2RXE8ovSJ4TCg"


# Initialize Rownd client
app.rownd_client = RowndClient(
    app_key="key_tuhke65w1oinga4mo46fxyky",
    app_secret="ras_ad22057b7d76c0e03112ad0fc40e1c152eab6a05fad43c2a",
    app_id="ras_ad22057b7d76c0e03112ad0fc40e1c152eab6a05fad43c2a",
    base_url="https://api.rownd.io"
)

@app.route("/validate")
async def validate_handler():
    """Validate endpoint that mirrors Go implementation"""
    token = request.headers.get('Authorization', '')
    if not token:
        return jsonify({
            "error": "Authentication required",
            "message": "No token provided"
        }), 401
    
    token = token.replace('Bearer ', '')
    
    try:
        validation = await app.rownd_client.auth.validate_token(token)
        return jsonify({
            "decoded_token": validation.decoded_token,
            "user_id": validation.user_id,
            "access_token": validation.access_token
        })
    except Exception as e:
        return jsonify({
            "error": "Invalid token",
            "message": str(e)
        }), 401

@app.route("/test-validate")
async def test_validate():
    """Test endpoint using our constant test token"""
    try:
        validation = await app.rownd_client.auth.validate_token(TEST_TOKEN)
        
        # Extract claims like in Go integration tests
        user_id = validation.decoded_token.get('https://auth.rownd.io/app_user_id')
        is_verified = validation.decoded_token.get('https://auth.rownd.io/is_verified_user')
        auth_level = validation.decoded_token.get('https://auth.rownd.io/auth_level')
        
        return jsonify({
            "valid": True,
            "user_id": user_id,
            "is_verified": is_verified,
            "auth_level": auth_level,
            "decoded_token": validation.decoded_token
        })
    except Exception as e:
        return jsonify({
            "valid": False,
            "error": str(e)
        }), 401

if __name__ == "__main__":
    app.run(debug=True)
