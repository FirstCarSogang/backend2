from celery import shared_task
from django.utils import timezone
from firstCarSogang_tickets.models import Ticket
from firstCarSogang_tickets.models import Day1Question, AfterDay1Question
from firstCarSogang_signuplogin.models import UserProfile

@shared_task
def match_users():
    current_time = timezone.now().time()
    if current_time.hour == 22 and current_time.minute == 0:
        for ticket in Ticket.objects.all():
            ticket.initiate_conversation()

@shared_task
def give_questions():
    current_time = timezone.now().time()
    if current_time.hour == 0 and current_time.minute == 0:
        for ticket in Ticket.objects.all():
            if ticket.filter(progressingDay=1).exists():
                Day1Question.objects.create()
            else:
                pass

@shared_task
def assign_tickets():
    users_needing_tickets = UserProfile.objects.filter(needs_ticket=True)    
    tickets_for_user = Ticket.objects.filter(users=users_needing_tickets)
    num_tickets_for_user = tickets_for_user.count()
    for user in users_needing_tickets:
        
        ticket = Ticket.objects.create(
            ticketNumber=num_tickets_for_user+1,
            progressingDay=1,  
            withWhom='',  
            isAnswered=False,
            choose=False,
        )
        
        ticket.users.add(user)
        ticket.save()

    return "Tickets assigned successfully"
