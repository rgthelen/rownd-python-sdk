from functools import wraps
from flask import request, jsonify, current_app
from .exceptions import RowndError

def require_auth(fetch_user: bool = False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"error": "No authorization header"}), 401

            token = auth_header.replace('Bearer ', '')
            
            try:
                token_info = current_app.rownd_client.validate_token(token)
                if fetch_user:
                    user = current_app.rownd_client.get_user(token_info.user_id)
                    kwargs['user'] = user
                kwargs['token_info'] = token_info
                return f(*args, **kwargs)
            except RowndError as e:
                return jsonify({"error": str(e)}), 401
            
        return decorated_function
    return decorator
