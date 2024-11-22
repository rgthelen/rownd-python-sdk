class RowndError(Exception):
    """Base exception for all Rownd errors"""
    pass

class AuthenticationError(RowndError):
    """Raised when authentication fails"""
    pass

class APIError(RowndError):
    """Raised when API calls fail"""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class ValidationError(RowndError):
    """Raised when validation fails"""
    pass

class ConfigurationError(RowndError):
    """Raised when configuration is invalid"""
    pass
