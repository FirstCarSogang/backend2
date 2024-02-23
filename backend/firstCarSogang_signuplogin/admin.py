# admin.py
from django.contrib import admin
from .models import UserProfile, EmailVerificationOTP

admin.site.register(UserProfile)
admin.site.register(EmailVerificationOTP)