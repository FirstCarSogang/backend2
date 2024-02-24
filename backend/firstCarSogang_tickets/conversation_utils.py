from django.contrib.auth import get_user_model
from firstCarSogang_tickets.models import Ticket
from random import sample

def initiate_conversation():
    User = get_user_model()
    users_with_tickets = User.objects.filter(useTicket=True)
    pairs = []
    odd_user = None
    users_with_tickets_list = list(users_with_tickets)
    sample(users_with_tickets_list, len(users_with_tickets_list))
    if len(users_with_tickets_list) % 2 == 0:
        for i in range(0, len(users_with_tickets_list), 2):
            pairs.append((users_with_tickets_list[i], users_with_tickets_list[i + 1]))
    else:
        odd_user = users_with_tickets_list.pop()

        for i in range(0, len(users_with_tickets_list) - 1, 2):
            pairs.append((users_with_tickets_list[i], users_with_tickets_list[i + 1]))

    for user1, user2 in pairs:
        ticket = Ticket.objects.create(
            progressingDay=0,  
            user=user1,
            withWhom=user2
        )
        ticket=Ticket.objects.create(
            progressingDay=0,  
            user=user2,
            withWhom=user1
        )
        user1.useTicket = False
        user1.ticketCount -= 1
        user2.useTicket = False
        user2.ticketCount -= 1
        user1.save()
        user2.save()
