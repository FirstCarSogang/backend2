from django.shortcuts import render,redirect
from django.views import View
from firstCarSogang_signuplogin.models import *
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
import random
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from firstCarSogang_signuplogin.utils import generate_access_token, generate_refresh_token
from .models import UserProfile
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
import json
import jwt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.http import FileResponse
import os
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# ===========================================================================================
@method_decorator(csrf_exempt, name='dispatch')
class Signup_register(View):
    def post(self, request):
        try:
            # POST 요청의 body에서 JSON 데이터 추출
            data = json.loads(request.body)

            existing_user = UserProfile.objects.filter(username=data['username']).exists()
            if existing_user:
                error_message = {"error": "이미 회원가입이 되어있는 학번입니다."}
                return JsonResponse(error_message, status=400)
            
            # 모델에 데이터 저장
            user_profile = UserProfile(
                name=data['name'],
                username=data['studentId'],
                kakaotalkID=data['kakaotalkID'],
                email=data['email'],
                photo1=data['photo1'],
                photo2=data['photo2'],
                photo3=data['photo3'],
                train=data['train'] == 'fast',  # 'fast'이면 True, 그 외에는 False
            )
            
            user_profile.save()

            # 응답 데이터 구성
            response_data = {
                'name': user_profile.name,
                'studentId': user_profile.username,
                'kakaotalkID': user_profile.kakaotalkID,
                'email': user_profile.email,
                'photo1': str(user_profile.photo1),  # 이미지는 일단 경로로 전송
                'photo2': str(user_profile.photo2),
                'photo3': str(user_profile.photo3),
                'train': 'fast' if user_profile.train else 'normal',  # Boolean 값을 문자열로 변환
                'date_joined': str(user_profile.date_joined),
                'last_login': str(user_profile.last_login),
                'ticketCount': user_profile.ticketCount,
                'useTicket': user_profile.useTicket,
                'message': '회원가입에 성공했습니다.'
            }

            # 응답 전송
            return JsonResponse(response_data, status=201)  # 201 Created 상태코드 반환
        
        except Exception as e:
            # 에러가 발생한 경우 에러 메시지와 함께 400 Bad Request 상태 코드 반환
            error_message = {"error": str(e)}
            return JsonResponse(error_message, status=400)
       
# ===========================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class mail_otp(View):
  
   def post(self, request):
        if request.method == 'POST':
            # POST 요청의 body에서 JSON 데이터 추출
            try:
                data = json.loads(request.body)
                email = data.get('email')
            except json.JSONDecodeError:
                return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)

            if email:
                # OTP 생성 및 저장
                otp_instance = EmailVerificationOTP.create(email)
                otp = otp_instance.otp
                
                # 생성된 OTP를 이메일로 전송
                subject = 'OTP Verification'
                message = f'Your OTP for registration is: {otp}'
                email_from = settings.EMAIL_HOST_USER
                email_to = [email]
                EmailMessage(subject, message, email_from, email_to).send()

                response_data = {
                    'success': True,
                    'message': 'OTP가 이메일로 전송되었습니다.',
                }
                return JsonResponse(response_data, status=200)
            else:
                # 이메일 주소가 제공되지 않은 경우
                return JsonResponse({'error': '이메일 주소가 제공되지 않았습니다.'}, status=400)
        else:
            # POST 요청이 아닌 경우
            return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=405)
        
 # ===========================================================================================      
         
        
@method_decorator(csrf_exempt, name='dispatch')
class otp_check(View):
   def post(self, request):
        if request.method == 'POST':
            # POST 요청의 body에서 JSON 데이터 추출
            try:
                data = json.loads(request.body)
                input_otp = data.get('input_otp')
                email = data.get('email')
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error_message': '잘못된 JSON 형식입니다.'}, status=400)

        if email and input_otp:
            try:
                # 해당 이메일과 OTP가 일치하는지 확인
                otp_instance = EmailVerificationOTP.objects.get(email=email, otp=input_otp)
                if otp_instance.is_valid():
                    return JsonResponse({'success': True, 'message': 'OTP 인증이 완료되었습니다.'}, status=200)
                else:
                    return JsonResponse({'success': False, 'message': 'OTP가 만료되었습니다.'}, status=400)
            except EmailVerificationOTP.DoesNotExist:
                return JsonResponse({'success': False, 'message': '유효하지 않은 OTP입니다.'}, status=400)
        else:
            return JsonResponse({'success': False, 'message': '이메일 주소와 OTP를 모두 제공해야 합니다.'}, status=400)
    
# ===========================================================================================   
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    
    def post(self, request):
        data = json.loads(request.body)
        username = data.get('studentId')
        password = data.get('password')

        
        # 사용자 조회
        try:
            user_profile = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            # 사용자가 존재하지 않을 경우
            return JsonResponse({'error': '존재하지 않는 학번입니다.'}, status=401)

        # 비밀번호 확인
        if password != user_profile.password:
            # 비밀번호가 일치하지 않을 경우
            return JsonResponse({'error': '비밀번호가 일치하지 않습니다.'}, status=401)

        # 로그인 성공 시 Access Token과 Refresh Token 발급
        access_token = generate_access_token(username)
        refresh_token = generate_refresh_token(username)

    # Refresh Token을 DB에 저장
        user_profile.refresh_token = refresh_token
        user_profile.save()

        response_data = {
            'accessToken': access_token,
            'refreshToken': refresh_token,
            'studentId': user_profile.username,
            'message': 'login.'
        }
        
        return JsonResponse(response_data, status=200)

    
    
# =========================================================================================== 
@csrf_exempt
def logout(request):
    if request.method == 'DELETE':
    # 헤더에서 Access Token 추출
        token = request.headers.get('Authorization', '').split()[1]

    # 토큰에서 사용자 정보 추출
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
       

        # 사용자의 refresh_token 초기화 (예시로 설정)
        try:
            user = UserProfile.objects.get(username=username)
            user.refresh_token = None  # refresh_token 초기화
            user.save()
            return JsonResponse({'message': '로그아웃되었습니다.'}, status=200)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)     
    
# ===========================================================================================
@method_decorator(csrf_exempt, name='dispatch')
class reset_otp(View):
    def post(self, request):
        if request.method == 'POST':
            # POST 요청의 body에서 JSON 데이터 추출
            try:
                data = json.loads(request.body)
                email = data.get('email')
            except json.JSONDecodeError:
                return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)

            
            if email :
            # 이메일이 데이터베이스에 있는지 확인합니다.
                user = UserProfile.objects.filter(email=email).first()

                if user:
                # OTP 생성
                    otp = ''.join([str(random.randint(0, 9)) for _ in range(5)])

                    # 사용자 객체에 OTP 저장
                    user.otp = otp
                    user.save()

                    # 생성된 OTP를 이메일로 전송
                    subject = '비밀번호 초기화를 위한 otp'
                    message = f'비밀번호 초기화를 위한 otp : {otp}'
                    email_from = settings.EMAIL_HOST_USER
                    email_to = [email]
                    EmailMessage(subject, message, email_from, email_to).send()


                    response_data = {
                        'success': True,
                        'message': 'OTP가 이메일로 전송되었습니다.'
                    }
                    return JsonResponse(response_data, status=200)

                else:
                    # 이메일이 데이터베이스에 없을 때
                    return JsonResponse({'error': '등록되지 않은 이메일입니다.'}, status=400)
            else:
                # 이메일 주소가 제공되지 않은 경우
                return JsonResponse({'error': '이메일 주소가 제공되지 않았습니다.'}, status=400)    

        else:
            # POST 요청이 아닌 경우
            error_message = "POST 요청이 필요합니다."
            return JsonResponse({"error_message": error_message}, status=400)
        
# ===========================================================================================
@method_decorator(csrf_exempt, name='dispatch')
class EnterOTPView(View):
    def post(self, request):
        # POST 요청의 body에서 JSON 데이터 추출
        try:
            data = json.loads(request.body)
            email = data.get('email')
            input_otp = data.get('input_otp')
        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
        
        if email and input_otp:
            # 이메일을 기반으로 사용자 조회
            user = UserProfile.objects.filter(email=email).first()

            # 사용자가 있는 경우
            if user:
                user_otp = user.otp
                
                if user_otp != input_otp:
                    # OTP가 일치하지 않는 경우
                    return JsonResponse({'error': '입력한 OTP가 유효하지 않습니다.'}, status=400)
                else:
                    # OTP가 일치하는 경우
                    return JsonResponse({'message': 'OTP가 인증되었습니다.'}, status=200)
            else:
                # 사용자가 존재하지 않는 경우
                return JsonResponse({'error': '존재하지 않는 사용자입니다.'}, status=404)
        else:
            # 이메일 또는 입력된 OTP가 없는 경우
            return JsonResponse({'error': '이메일과 OTP를 모두 제공해야 합니다.'}, status=400)
# ===========================================================================================
@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetView(View):
    def post(self, request):
        # POST 요청의 body에서 JSON 데이터 추출
        try:
            data = json.loads(request.body)
            email = data.get('email')
            new_password = data.get('new_password')
            confirm_new_password = data.get('confirm_new_password')
        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 JSON 형식입니다.'}, status=400)
        
        # 이메일과 새로운 비밀번호, 확인 비밀번호가 모두 제공되었는지 확인
        if email and new_password and confirm_new_password:
            try:
                user = UserProfile.objects.get(email=email)
            except UserProfile.DoesNotExist:
                # 이메일에 해당하는 사용자가 없는 경우
                return JsonResponse({'error': '존재하지 않는 사용자입니다.'}, status=404)
            
            # 새로운 비밀번호와 확인 비밀번호가 일치하는지 확인
            if new_password != confirm_new_password:
                return JsonResponse({'error': '비밀번호와 확인 비밀번호가 일치하지 않습니다.'}, status=400)
            
            # 기존 비밀번호와 새로운 비밀번호가 일치하는지 확인
            if new_password == user.password:
                return JsonResponse({'error': '새로운 비밀번호는 기존 비밀번호와 동일할 수 없습니다.'}, status=400)
            
            # 모든 검증을 통과한 경우
            user.password = new_password
            user.save()
            
            # 비밀번호 변경 완료 메일 전송
            html_message = "비밀번호 변경이 완료되었습니다. 본인이 아닐 경우 비밀번호를 변경해주세요"
            subject = "첫차 서강 비밀번호 변경 완료"
            email_from = settings.EMAIL_HOST_USER
            email_to = [email]
            message = EmailMessage(subject, html_message, email_from, email_to)
            message.send()
            
            return JsonResponse({'message': '비밀번호가 성공적으로 변경되었습니다.'}, status=200)
        else:
            return JsonResponse({'error': '이메일과 새로운 비밀번호, 확인 비밀번호를 모두 제공해야 합니다.'}, status=400)
# ===========================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class MyPageView(View):
    def get(self, request):
        
        # 헤더에서 Bearer 토큰 추출
        token = request.headers.get('Authorization').split()[1]

        # 토큰에서 사용자 정보 추출
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
       
        
        # 사용자 정보 가져오기
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # 응답 데이터 구성
        response_data = {
            'studentId': user.username,
            'name': user.name,
            'train': user.train,
            # 필요한 다른 정보도 추가 가능
        }

        # 응답 반환
        return JsonResponse(response_data, status=200)
    
# ===========================================================================================
@csrf_exempt
def toggle_train_status(request):
    if request.method == 'POST':
        # 요청으로부터 JSON 데이터 추출
        try:
            data = json.loads(request.body)
            train_status = data.get('train')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        # 헤더에서 Access Token을 추출
        token = request.headers.get('Authorization').split()[1]
        
         # 토큰에서 사용자 정보 추출
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
       
        
        # 사용자 정보 가져오기
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        if train_status == 'fast':
            train_value = True
        elif train_status == 'normal':
            train_value = False
        # 유저 정보에서 train 값을 변경
        user.train = train_value
        user.save()

        # 변경된 train 값과 메시지를 응답으로 보냄
        response_data = {
            'train': user.train,
            'message': 'Train status successfully toggled.',
        }
        return JsonResponse(response_data, status=200)

    else:
        return JsonResponse({'error': 'POST method required.'}, status=405)
    
    
# ===========================================================================================
@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        # 요청의 본문에서 JSON 데이터 추출
        try:
            data = json.loads(request.body)
            password = data.get('password')
            new_password = data.get('new_password')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request body.'}, status=400)
        
        # 헤더에서 Access Token을 추출
        token = request.headers.get('Authorization').split()[1]
        
         # 토큰에서 사용자 정보 추출
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
       
    
        # 사용자 정보 가져오기
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        if password == new_password :
            return JsonResponse({'error': '기존 비밀번호 입력과 새로운 비밀번호 입력이 동일합니다.'}, status=400)
         # 기존 비밀번호와 새로운 비밀번호가 일치하는지 확인
        else:
            if password == user.password:
                # 모든 검증을 통과한 경우  
                user.password = new_password
                user.save()
                
                response_data = {
                 'message': '비밀번호가 변경되었습니다.'
                 }
                return JsonResponse(response_data, status=200)
            else :
                 return JsonResponse({'error': '기존 비밀번호가 일치하지 않습니다.'}, status=400)


# ===========================================================================================         
@csrf_exempt
def change_kakaotalkid(request):
    if request.method == 'POST':
        # 요청의 본문에서 JSON 데이터 추출
        try:
            data = json.loads(request.body)
            kakaotalkID = data.get('kakaotalkID')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request body.'}, status=400)
        
        # 헤더에서 Access Token을 추출
        token = request.headers.get('Authorization').split()[1]
        
         # 토큰에서 사용자 정보 추출
       
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
       
    
        # 사용자 정보 가져오기
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
      
        if kakaotalkID != user.kakaotalkID:
            # 모든 검증을 통과한 경우  
            user.kakaotalkID = kakaotalkID
            user.save()
                
            response_data = {
                 'message': '카카오톡아이디가 변경되었습니다.'
                 }
            return JsonResponse(response_data, status=200)
        else :
            return JsonResponse({'error': '기존의 카카오톡 아이디와 일치합니다.'}, status=400)
        
                         

# ===========================================================================================                 
             
             
@method_decorator(csrf_exempt, name='dispatch')
class kakaotalk(View):
    def get(self, request):
        # 헤더에서 Bearer 토큰 추출
        token = request.headers.get('Authorization').split()[1]

        # 토큰에서 사용자 정보 추출
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
       
        
        # 사용자 정보 가져오기
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # 응답 데이터 구성
        response_data = {
            'kakaotalkID': user.kakaotalkID
        }

        # 응답 반환
        return JsonResponse(response_data, status=200)
    
    
    
    
# ===========================================================================================  
@csrf_exempt
def useTicket(request):
    if request.method == 'POST':
        # 요청으로부터 JSON 데이터 추출
        try:
            data = json.loads(request.body)
            useTicket = data.get('useTicket')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        # 헤더에서 Access Token을 추출
        token = request.headers.get('Authorization').split()[1]
        
         # 토큰에서 사용자 정보 추출
       
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
       
        
        # 사용자 정보 가져오기
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
      
        user.useTicket = useTicket
        user.save()

        # 변경된 useTicket 값과 메시지를 응답으로 보냄
        response_data = {
            'useTicket': user.useTicket,
            'message': '티켓 사용 변경 완료.',
        }
        return JsonResponse(response_data, status=200)

    else:
        return JsonResponse({'error': 'POST method required.'}, status=405)
    
# ===========================================================================================    
class matching(View):
    def get(self, request):
        # 헤더에서 Bearer 토큰 추출
        token = request.headers.get('Authorization').split()[1]

        # 토큰에서 사용자 정보 추출
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
      
        
        # 사용자 정보 가져오기
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404) 
  
        # 사용자의 사진 URL 가져오기
        photo1_url = user.photo1.url if user.photo1 else None
        photo2_url = user.photo2.url if user.photo2 else None
        photo3_url = user.photo3.url if user.photo3 else None

        # 추가 정보 가져오기
        ticket_count = user.ticketCount
        use_ticket = user.useTicket

        # 모든 정보를 JSON 응답에 담아 반환
        response_data = {
            'photo1_url': photo1_url,
            'photo2_url': photo2_url,
            'photo3_url': photo3_url,
            'ticket_count': ticket_count,
            'use_ticket': use_ticket
        }
        return JsonResponse(response_data, status=200)

# ===========================================================================================    
@csrf_exempt
def update_user_photos1(request):
    if request.method == 'POST':
        # 헤더에서 Access Token을 추출
        token = request.headers.get('Authorization', '').split()[1]
        
        # 토큰에서 사용자 정보 추출
      
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
       
        
        # 사용자 정보 가져오기
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # 프론트엔드에서 전송된 사진 파일 받기
        photo1_file = request.FILES.get('photo')
        
        # 사용자의 기존 사진 파일 업데이트
        if photo1_file:
            user.photo1.save(photo1_file.name, photo1_file)

        
        # 업데이트된 정보 저장
        user.save()
        
        return JsonResponse({'message': '사진이 업데이트되었습니다.'}, status=200)
    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
    

 # ===========================================================================================   
    
@csrf_exempt
def update_user_photos2(request):
    if request.method == 'POST':
        # 헤더에서 Access Token을 추출
        token = request.headers.get('Authorization', '').split()[1]
        
        # 토큰에서 사용자 정보 추출
      
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
       
        
        # 사용자 정보 가져오기
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # 프론트엔드에서 전송된 사진 파일 받기
        photo2_file = request.FILES.get('photo')
        
        # 사용자의 기존 사진 파일 업데이트
        if photo2_file:
            user.photo2.save(photo2_file.name, photo2_file)
    
        
        # 업데이트된 정보 저장
        user.save()
        
        return JsonResponse({'message': '사진이 업데이트되었습니다.'}, status=200)
    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)

 # ===========================================================================================       
@csrf_exempt
def update_user_photos3(request):
    if request.method == 'POST':
        # 헤더에서 Access Token을 추출
        token = request.headers.get('Authorization', '').split()[1]
        
        # 토큰에서 사용자 정보 추출
      
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']
       
        
        # 사용자 정보 가져오기
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # 프론트엔드에서 전송된 사진 파일 받기
        photo3_file = request.FILES.get('photo')
        
        # 사용자의 기존 사진 파일 업데이트
        if photo3_file:
            user.photo3.save(photo3_file.name, photo3_file)
        
        # 업데이트된 정보 저장
        user.save()
        
        return JsonResponse({'message': '사진이 업데이트되었습니다.'}, status=200)
    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
    




 # ===========================================================================================      
@csrf_exempt
def token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            refresh_token =data.get('refresh_token')
            access_token = data.get('access_token')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request body.'}, status=400)
        
        if not refresh_token or not access_token:
            return JsonResponse({'error': 'Refresh Token과 Access Token을 모두 제공해야 합니다.'}, status=400)
        
        # Refresh Token의 유효성 검증
        #payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        username = payload['username']

        user = UserProfile.objects.get(username=username)
        user_refresh_token = user.refresh_token
            
        if user_refresh_token == refresh_token:
            decoded_token = jwt.decode(user_refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            expiration_time = datetime.utcfromtimestamp(decoded_token['exp'])
            if expiration_time < datetime.utcnow():
            # refresh_token의 유효 기간이 지났을 경우
                return JsonResponse({'error': 'Expired Refresh Token, Expired Access Token'}, status=401)
            else:
            # refresh_token의 유효 기간이 지나지 않았을 경우
            # 새로운 Access Token 생성
                new_access_token = generate_access_token(username)
                return JsonResponse({'access_token': new_access_token}, status=200) 
    else:
        return JsonResponse({'error': 'POST 메서드만 허용됩니다.'}, status=405)        

from django.http import HttpResponse
from .tasks import send_user_info_to_server

def send_user_info(request):
    send_user_info_to_server()
    return HttpResponse("User info sent to server successfully.")
