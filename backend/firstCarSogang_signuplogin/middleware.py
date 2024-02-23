from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .utils import verify_token, generate_access_token, generate_refresh_token
from .models import UserProfile
import jwt
from django.conf import settings
from datetime import datetime

class TokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 요청 헤더에서 Access Token 추출
        access_token = request.headers.get('Authorization', '')
        
        # 로그인 시에는 토큰 검증 생략
        if not access_token.startswith('Bearer'):
            return
        
        if access_token:
            access_token = access_token.split(' ')[1]
        else:
            return JsonResponse({'error': 'Authorization 헤더에 Access Token이 필요합니다.'}, status=401) 
        
        # Access Token 유효성 검증
        payload = verify_token(access_token)
        
        try:
            if payload:
            
            #refresh_token 유효성 확인
                token = request.headers.get('Authorization').split()[1]
            # 토큰에서 사용자 정보 추출
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                username = payload['username']
            
                try:
                    user = UserProfile.objects.get(username=username)
                except UserProfile.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=404)
            
            #유저의 refresh_token 유효성 확인
            #refresh_token 만료시 새로운 refreshtoken 생성후 유저 db에 저장
                refresh_token = user.refresh_token
    
                if refresh_token:
                    decoded_token = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
                    expiration_time = datetime.utcfromtimestamp(decoded_token['exp'])
                    if expiration_time < datetime.utcnow():
                # refresh_token의 유효 기간이 지났을 경우
                        new_refresh_token = generate_refresh_token(username)
                        user.refresh_token = new_refresh_token
                        user.save()
                    else:
                    # refresh_token의 유효 기간이 지나지 않았을 경우
                        return 

            else:
            #refresh_token 유효성 확인
                token = request.headers.get('Authorization').split()[1]
            # 토큰에서 사용자 정보 추출
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                username = payload['username']
            
                try:
                    user = UserProfile.objects.get(username=username)
                except UserProfile.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=404)
                refresh_token = user.refresh_token
    
                if refresh_token:
                    decoded_token = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
                    expiration_time = datetime.utcfromtimestamp(decoded_token['exp'])
                    if expiration_time < datetime.utcnow():
                # refresh_token의 유효 기간이 지났을 경우
                        return JsonResponse({'error': 'Expired Refresh Token, Expired Access Token'}, status=401)
                    else:
                    # refresh_token의 유효 기간이 지나지 않았을 경우
                        return JsonResponse({'error': 'Expired Access Token'}, status=401)
        except jwt.ExpiredSignatureError:
            # 토큰이 만료된 경우
            return JsonResponse({'error': 'Expired Access Token'}, status=401)
        except jwt.InvalidTokenError:
            # 유효하지 않은 토큰인 경우
            return JsonResponse({'error': 'Invalid Token'}, status=401)
                