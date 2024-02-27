
from django.db import models
from firstCarSogang_signuplogin.models import UserProfile
from django.db.models import JSONField
from datetime import datetime 


class Ticket(models.Model):
    ticketNumber = models.IntegerField(verbose_name="티켓 번호", null=True, blank=True)
    progressingDay = models.IntegerField(verbose_name="진행중인 날짜")
    isAnswered = models.BooleanField(verbose_name="답변 여부", default=False)
    choose = models.BooleanField(verbose_name="선택 여부", default=False)
    day_question = JSONField(null=True, blank=True)
    user = models.ForeignKey(UserProfile, verbose_name="내 티켓 아이디", on_delete=models.CASCADE, null=True, blank=True, related_name='tickets')
    withWhom = models.ForeignKey(UserProfile, verbose_name="상대편 티켓 아이디", on_delete=models.CASCADE, null=True, blank=True, related_name='tickets_with_whom')

    def __str__(self):
        return f"{self.ticketNumber}: {self.progressingDay} 일째 대화"

class Comment(models.Model):
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"Comment by {self.from_user} at {self.created_at}"

class Day1Question(models.Model):
    question = models.CharField(max_length=1000, verbose_name="질문")
    placeholder = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000, verbose_name="대답", blank=True, null=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='daily_question')
    comments = models.ManyToManyField(Comment, related_name='day1_comments')
    
    def __str__(self):
        return f"Question: {self.question} - User: {self.user}"

class AfterDay1Question(models.Model):
    question_id = models.IntegerField(verbose_name="질문 ID", unique=True)
    question = models.CharField(max_length=1000, verbose_name="질문1")
    placeholder = models.CharField(max_length=1000)
    multipleChoiceAnswer1 = models.CharField(max_length=1000, verbose_name="객관식 답변1")
    multipleChoiceAnswer2 = models.CharField(max_length=1000, verbose_name="객관식 답변2")
    multipleChoiceAnswer3 = models.CharField(max_length=1000, verbose_name="객관식 답변3")
    multipleChoiceAnswer4 = models.CharField(max_length=1000, verbose_name="객관식 답변4")
    multipleChoiceAnswer5 = models.CharField(max_length=1000, verbose_name="객관식 답변5")
    answer = models.CharField(verbose_name="주관식 답변", blank=True, null=True, max_length=1000)
    answer2=models.IntegerField(default=1)
    comments = models.ManyToManyField(Comment, related_name='after_day1_comments')
    def __str__(self):
        return f"AfterDay1Question {self.question_id}: {self.question}"
    