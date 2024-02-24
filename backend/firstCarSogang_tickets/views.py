from django.shortcuts import render, redirect
from .models import Day1Question,Ticket,AfterDay1Question,Comment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
import json

@csrf_exempt  
def slow_train(request):
    if request.method == 'GET':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data in the request body'}, status=400)
        
        username = data.get('username', '') 
        
        if username:
            try:
                user_profile = UserProfile.objects.get(username=username)
                ticket = Ticket.objects.filter(user=user_profile).first()              
                if ticket:
                    return JsonResponse({'ticket_id': ticket.id, 'success': 'Ticket retrieved successfully'}, status=200)
                else:
                    return JsonResponse({'success': 'No ticket found for the user'}, status=200)
            except UserProfile.DoesNotExist:
                return JsonResponse({'error': 'User with the provided username does not exist'}, status=404)
        else:
            return JsonResponse({'error': 'Username not provided in the JSON data'}, status=400)

    elif request.method == 'DELETE':
        username = request.GET.get('username', '')
        
        if username:
            try:
                user_profile = UserProfile.objects.get(username=username)
                ticket = Ticket.objects.filter(user=user_profile).first()
                
                if ticket:
                    ticket.delete()
                    return JsonResponse({'success': 'Ticket deleted successfully'}, status=200)
                else:
                    return JsonResponse({'success': 'No ticket found for the user'}, status=200)
            except UserProfile.DoesNotExist:
                return JsonResponse({'error': 'User with the provided username does not exist'}, status=404)
        else:
            return JsonResponse({'error': 'Username not provided in the GET parameters'}, status=400)
            
    else:
        return JsonResponse({'error': 'Only GET and DELETE requests are accepted for this endpoint'}, status=405)

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