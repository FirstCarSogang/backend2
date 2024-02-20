from django.shortcuts import render, redirect
from .models import Day1Question,Ticket,AfterDay1Question,Comment
from django.http import JsonResponse

def slow_train(request):
    username = request.user.username
    ticket = Ticket.objects.filter(ticketNumber=username)
    if request.method == 'DELETE':
            ticket.delete()
            return JsonResponse({'success': 'Ticket deleted successfully'}, status=200)
        
    if request.method == 'POST':
            day = int(request.POST.get('day'))
            choose = bool(request.POST.get('choose'))
            
            if day == 4:
                ticket.choose = choose
                ticket.save()
                return JsonResponse({'success': 'Choose field updated successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Choose field can only be updated on day 4'}, status=400)
    data = {
        'day1_questions': [
            {
                'id': question.id,
                'question': question.question,
                'placeholder': question.placeholder,
            }
            for question in ticket
        ]
    }
    return JsonResponse(data)

def get_ticket_info(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
        
        with_whom = ticket.withWhom
        if with_whom is not None:
            associated_ticket = Ticket.objects.get(pk=with_whom)
            data = {
                'ticket_id': associated_ticket.id,
                'ticket_number': associated_ticket.ticketNumber,
                'progressing_day': associated_ticket.progressingDay,
                'is_answered': associated_ticket.isAnswered,
                'choose': associated_ticket.choose,
                'day_question': associated_ticket.dayQuestion,
                'with_whom': associated_ticket.withWhom
            }
            
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'No associated ticket found'}, status=404)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket does not exist'}, status=404)

def get_ticket_questions(request, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
        day1_question_id = ticket.DayQuestion[0] if ticket.DayQuestion else None
        
        day1_question = Day1Question.objects.get(pk=day1_question_id) if day1_question_id else None
        after_day1_questions = AfterDay1Question.objects.filter(pk__in=ticket.DayQuestion[1:])
        
        serialized_day1_question = {
            'id': day1_question.id if day1_question else None,
            'question': day1_question.question if day1_question else None,
            'placeholder': day1_question.placeholder if day1_question else None,
            'answer': day1_question.answer if day1_question else None,
            } if day1_question else None
        serialized_after_day1_questions = [
            {
                'id': question.id,
                'question1': question.question1,
                'placeholder1': question.placeholder1,
                'answer': question.answer,
            }
            for question in after_day1_questions
        ]
        
        data = {
            'day1_question': serialized_day1_question,
            'after_day1_questions': serialized_after_day1_questions
        }
        
        return JsonResponse(data)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket does not exist'}, status=404)
    

from django.views.decorators.csrf import csrf_exempt  
@csrf_exempt  
@csrf_exempt
def get_day_questions(request, ticket_number, day):
    try:
        ticket = Ticket.objects.get(ticketNumber=ticket_number)
        if day < 1 or day > len(ticket.DayQuestion):
            return JsonResponse({'error': 'Invalid day'}, status=400)
        
        question_id = ticket.DayQuestion[day - 1]
        
        if isinstance(question_id, int):
            question = Day1Question.objects.get(pk=question_id)
        else:
            question = AfterDay1Question.objects.get(pk=question_id)
        
        if request.method == 'POST':
            answer = request.POST.get('answer')
            comment_id = request.POST.get('comment_id')
            if answer:
                question.answer = answer
                question.save()
            elif comment_id:
                comment = Comment.objects.get(pk=comment_id)
                reply_content = request.POST.get('reply_content')
                if reply_content:
                    reply = Comment(content=reply_content, from_user=request.user)
                    reply.save()
                    comment.replies.add(reply)
                    comment.save()
                else:
                    return JsonResponse({'error': 'Reply content is missing'}, status=400)
            else:
                return JsonResponse({'error': 'No answer or reply provided'}, status=400)
        
        serialized_question = {
            'id': question.id,
            'question': question.question,
            'placeholder': question.placeholder,
            'answer': question.answer,
        }
        
        data = {
            'ticket_number': ticket_number,
            'day': day,
            'question': serialized_question
        }
        
        return JsonResponse(data)
    
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket does not exist'}, status=404)
    except (Day1Question.DoesNotExist, AfterDay1Question.DoesNotExist):
        return JsonResponse({'error': 'Question does not exist'}, status=404)