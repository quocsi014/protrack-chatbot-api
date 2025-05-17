import jwt
from jwt import PyJWTError, ExpiredSignatureError, InvalidTokenError


def verify_jwt(token: str, secret_key: str, algorithms: list = ["HS256"]):
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except InvalidTokenError:
        raise ValueError("Invalid token")
    except PyJWTError as e:
        raise ValueError(f"Token verification failed: {str(e)}")
