import jwt
from datetime import datetime, timedelta
from django.conf import settings

def generate_access_token(username):
    """
    사용자의 학번을 받아서 Access Token을 생성합니다.
    """
    
    # 토큰 만료 시간 설정 (예: 현재 시간으로부터 5시간 후)
    expiration_time = datetime.utcnow() + timedelta(hours=5)
    
    # Access Token의 payload에는 사용자의 학번과 만료 시간을 포함시킵니다.
    payload = {
        'username': username,
        'exp': expiration_time
    }
        
    # JWT를 사용하여 Access Token을 생성합니다.
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return access_token

def generate_refresh_token():
    """
    Refresh Token을 생성합니다.
    """
     # 토큰 만료 시간 설정 (예: 현재 시간으로부터 2주 후)
    expiration_time = datetime.utcnow() + timedelta(weeks=2)
    
    # 임의의 문자열을 사용하여 Refresh Token을 생성합니다.
    refresh_token = jwt.encode({'exp': expiration_time}, settings.SECRET_KEY, algorithm='HS256')
    
    return refresh_token

def verify_token(token):
    """
    토큰의 유효성을 확인합니다.
    """
    try:
        # 토큰을 해독하여 payload를 가져옵니다.
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        # 만료된 토큰인 경우
        return None
    except jwt.InvalidTokenError:
        # 유효하지 않은 토큰인 경우
        return None