from django.urls import path
from .views import slow_train, get_ticket_questions ,get_day_questions

urlpatterns = [
    path('slowtrain/<int:ticket_id>/', get_ticket_questions, name='chatroom'),
    path('slowtrain/', slow_train, name="slow_train"),
    path('slowtrain/<int:ticket_number>/day<int:day>/',get_day_questions, name='get_day_questions'),

]
