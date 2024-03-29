from django.db import models
from django.utils import timezone
import random
import string
from django.contrib.auth.models import AbstractUser
from random import sample

def user_directory_path(instance, filename):
    # 파일 업로드 경로를 사용자 이름(username) 기반으로 지정
    return 'user_profile/{0}/{1}'.format(instance.username, filename)

class UserProfile(AbstractUser):
    username = models.CharField(max_length=10, unique=True)  # 기본값으로 빈 문자열을 설정
    name = models.CharField(max_length=100)
    kakaotalkID = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    photo1 = models.ImageField(upload_to=user_directory_path,null=True)
    photo2 = models.ImageField(upload_to=user_directory_path,null=True)
    photo3 = models.ImageField(upload_to=user_directory_path,null=True)
    password = models.CharField(max_length=25)
    train = models.BooleanField(default=True)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    otp = models.CharField(max_length=5,default='20249')
    ticketCount=models.IntegerField(default=3)
    useTicket=models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    # Refresh Token 필드 추가
    refresh_token = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:  
            self.is_staff = False  # 기본적으로 staff status를 False로 설정
            self.is_superuser = False  # 기본적으로 superuser status를 False로 설정
        super().save(*args, **kwargs)
    


class EmailVerificationOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_or_update(cls, email):
        # 이메일로 검색하여 해당 이메일의 모든 OTP 객체를 가져옴
        otp_instances = cls.objects.filter(email=email)
        
        # 만약 해당 이메일에 대한 OTP 객체가 존재한다면
        if otp_instances.exists():
            # 모든 객체를 삭제
            otp_instances.delete()

        # 새로운 OTP 생성
        otp = generate_otp()
        # 생성된 OTP와 이메일 주소로 객체 생성
        otp_create = cls.objects.create(email=email, otp=otp)
        return otp_create

    def is_valid(self):
        # 만료 시간 확인 (예: 5분)
        expiration_time = timezone.now() - timezone.timedelta(minutes=5)
        return self.created_at >= expiration_time

    def __str__(self):
        return self.email

def generate_otp(length=5):
    # 사용할 문자열 세트 정의 (예: 숫자)
    characters = string.digits
    # 임시로 생성된 OTP 저장
    otp = ''.join(random.choices(characters, k=length))

    return otp

