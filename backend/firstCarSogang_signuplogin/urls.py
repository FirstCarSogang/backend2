from django.urls import path
from firstCarSogang_signuplogin.views import *
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('login',LoginView.as_view(), name='LoginView'),
    path('logout',logout, name='logout'),
    path('signup/register',Signup_register.as_view(),name='Signup_register'),
    path('signup/mail_otp', mail_otp.as_view(), name='smail_otp'),
    path('signup/otp_check', otp_check.as_view(), name='otp_check'),
    
    
    path('forgetpassword1', reset_otp.as_view(), name='reset_otp'),
    path('forgetpassword2', EnterOTPView.as_view(), name='enter_otp'),
    path('forgetpassword3', PasswordResetView.as_view(), name='password_reset'),
    
    path('setting',MyPageView.as_view(), name= 'setting'),
    path('setting/train',toggle_train_status, name= 'toggle_train_status'),
    path('setting/changepassword',change_password, name= 'change_password'),
    path('setting/changekakaotalkid',change_kakaotalkid, name= 'changekakaotalkid'),
    path('setting/kakaotalkid',kakaotalk.as_view(), name= 'kakaotalkid'),
    
    
    
    path('matching/ticketuse',useTicket, name= 'useTicket'),
    path('matching',matching.as_view(), name= 'matching'),
    path('matching/changephoto/1',update_user_photos1, name= 'changephoto1'),
    path('matching/changephoto/2',update_user_photos2, name= 'changephoto2'),
    path('matching/changephoto/3',update_user_photos3, name= 'changephoto3'),

    path('token',token, name='token'),
    path('send_user_info/', views.send_user_info, name='send_user_info'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)