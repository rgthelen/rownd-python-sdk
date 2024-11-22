from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class TokenValidationResponse:
    decoded_token: Dict[str, Any]
    access_token: str

@dataclass
class JWKS:
    keys: List[Dict[str, Any]]

@dataclass
class WellKnownConfig:
    issuer: str
    jwks_uri: str
    token_endpoint: str
    userinfo_endpoint: Optional[str] = None
    response_types_supported: Optional[List[str]] = None
    id_token_signing_alg_values_supported: Optional[List[str]] = None
    grant_types_supported: Optional[List[str]] = None
    subject_types_supported: Optional[List[str]] = None
    scopes_supported: Optional[List[str]] = None
    token_endpoint_auth_methods_supported: Optional[List[str]] = None
    claims_supported: Optional[List[str]] = None
    code_challenge_methods_supported: Optional[List[str]] = None
    introspection_endpoint_auth_methods_supported: Optional[List[str]] = None
    revocation_endpoint_auth_methods_supported: Optional[List[str]] = None
    request_parameter_supported: Optional[bool] = None
    request_object_signing_alg_values_supported: Optional[List[str]] = None