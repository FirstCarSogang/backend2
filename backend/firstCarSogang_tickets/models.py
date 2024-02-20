from django.db import models
from firstCarSogang_signuplogin.models import UserProfile
from django.contrib.postgres.fields import ArrayField
from random import sample
from datetime import datetime 

class Ticket(models.Model):
    ticketNumber = models.IntegerField(verbose_name="티켓 번호")
    progressingDay = models.IntegerField(verbose_name="진행중인 날짜")
    isAnswered = models.BooleanField(verbose_name="답변 여부", default=False)
    choose = models.BooleanField(verbose_name="선택 여부", default=False)
    dayQuestion=ArrayField(models.IntegerField(),null=True,blank=True)
    user = models.ForeignKey(UserProfile, verbose_name="내 티켓 아이디", on_delete=models.CASCADE, null=True, blank=True, related_name='tickets')
    withWhom=models.IntegerField(verbose_name="상대편 티켓 아이디",null=True,blank=True)
    def __str__(self):
        return f"{self.ticketNumber}: {self.progressingDay} 일째 대화"

    def initiate_conversation(self):
        users_with_tickets = self.users.filter(userTicket=True)
        pairs = []
        odd_user = None
        
        users_with_tickets_list = list(users_with_tickets)
        sample(users_with_tickets_list, len(users_with_tickets_list))  # Shuffling the list
        
        if len(users_with_tickets_list) % 2 == 0:
            for i in range(0, len(users_with_tickets_list), 2):
                pairs.append((users_with_tickets_list[i], users_with_tickets_list[i + 1]))
        else:
            odd_user = users_with_tickets_list.pop()

            for i in range(0, len(users_with_tickets_list) - 1, 2):
                pairs.append((users_with_tickets_list[i], users_with_tickets_list[i + 1]))

        for user1, user2 in pairs:
            user1.userTicket = False
            user1.ticketCount -= 1
            user2.userTicket = False
            user2.ticketCount -= 1
            user1.save()
            user2.save()

class Comment(models.Model):
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)


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