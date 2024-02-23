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

def generate_refresh_token(username):
    """
    Refresh Token을 생성합니다.
    """
     # 토큰 만료 시간 설정 (예: 현재 시간으로부터 2주 후)
    expiration_time = datetime.utcnow() + timedelta(weeks=2)
    payload = {
        'username': username,
        'exp': expiration_time
    }
    # 임의의 문자열을 사용하여 Refresh Token을 생성합니다.
    refresh_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    return refresh_token

def verify_token(token):
    """
    토큰의 유효성을 확인합니다.
    """
    try:
        # 토큰을 디코딩하여 payload를 가져옵니다.
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        
        # 유효 기간 확인
        expiration_time = datetime.utcfromtimestamp(decoded_token['exp'])
        if expiration_time < datetime.utcnow():
            # 만료된 토큰인 경우
            return None
        else:
            # 유효한 토큰인 경우 payload를 반환합니다.
            return decoded_token
    except jwt.InvalidTokenError:
        # 유효하지 않은 토큰인 경우
        return None