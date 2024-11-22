class RowndError(Exception):
    """Base exception for all Rownd errors"""
    pass

class AuthenticationError(RowndError):
    """Raised when authentication fails"""
    pass

class APIError(RowndError):
    """Raised when API calls fail"""
    pass