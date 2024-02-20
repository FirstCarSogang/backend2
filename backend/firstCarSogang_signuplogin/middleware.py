from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .utils import verify_token, generate_access_token, generate_refresh_token

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
        
        if payload:
            # Access Token이 유효한 경우, 요청에 사용자 정보 추가
            request.user = payload['username']
        else:
            # Access Token이 유효하지 않은 경우, Refresh Token을 확인하여 갱신
            refresh_token = request.headers.get('Refresh-Token', '')
            payload = verify_token(refresh_token)
            if payload:
                # Refresh Token이 유효한 경우, 새로운 Access Token 발급
                access_token, _ = generate_access_token(payload['username'])
                # 새로운 Access Token을 응답 헤더에 추가
                request.headers['Authorization'] = f'Bearer {access_token}'
            else:
                # Refresh Token도 만료된 경우, 에러 응답 반환
                return JsonResponse({'error': 'Refresh Token이 만료되었습니다.'}, status=401)
