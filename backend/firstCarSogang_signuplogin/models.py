from django.db import models
from django.utils import timezone
import random
import string
from django.contrib.auth.models import AbstractUser

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
    useTicket=models.BooleanField(default=False)
      
      
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
    def create(cls, email):
        # 새로운 OTP 생성
        otp = generate_unique_otp()
        # 생성된 OTP와 이메일 주소로 객체 생성
        return cls.objects.create(email=email, otp=otp)

    def is_valid(self):
        # 만료 시간 확인 (예: 5분)
        expiration_time = timezone.now() - timezone.timedelta(minutes=5)
        return self.created_at >= expiration_time

    def __str__(self):
        return self.email
    
def generate_unique_otp(length=5):
    # 사용할 문자열 세트 정의 (예: 숫자)
    characters = string.digits
    # 임시로 생성된 OTP 저장
    otp = ''.join(random.choices(characters, k=length))

    return otp



