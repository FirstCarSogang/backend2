from django.core.files.uploadedfile import SimpleUploadedFile
import requests

# 모델에서 유저 정보를 가져올 때 사용할 함수
def get_user_info():
    from .models import UserProfile  # UserProfile 모델을 import

    # userTicket이 True인 유저 필터링
    users = UserProfile.objects.filter(useTicket=True)

    # 각 유저의 정보를 가져와서 반환
    user_info_list = []
    for user in users:
        user_info = {
            'username': user.username,
            'photo1': user.photo1,
            'photo2': user.photo2,
            'photo3': user.photo3,
        }
        user_info_list.append(user_info)

    return user_info_list

# 모델 서버로 유저 정보를 전송하는 함수
def send_user_info_to_server():
    user_info_list = get_user_info()  # 유저 정보 가져오기

    # 모델 서버의 엔드포인트 URL
    model_server_url = 'https://aipubdev.sogang.ten1010.io/'

    # 가져온 각 유저 정보를 모델 서버로 전송
    for user_info in user_info_list:
        # 파일 업로드를 위한 파일 객체 생성
        photo1_file = None
        photo2_file = None
        photo3_file = None
        if user_info['photo1']:
            photo1_file = open(user_info['photo1'].path, 'rb')
        if user_info['photo2']:
            photo2_file = open(user_info['photo2'].path, 'rb')
        if user_info['photo3']:
            photo3_file = open(user_info['photo3'].path, 'rb')

        # 파일 객체를 requests의 files 파라미터에 전달
        files = {
            'photo1': photo1_file,
            'photo2': photo2_file,
            'photo3': photo3_file,
        }

        # 유저 정보와 파일 객체를 함께 POST 요청으로 모델 서버에 전송
        response = requests.post(model_server_url, data=user_info, files=files)

        # 파일 객체 닫기
        if photo1_file:
            photo1_file.close()
        if photo2_file:
            photo2_file.close()
        if photo3_file:
            photo3_file.close()

        # 응답 처리
        if response.status_code == 200:
            print(f"User info for {user_info['username']} sent successfully.")
        else:
            print(f"Failed to send user info for {user_info['username']}.")

