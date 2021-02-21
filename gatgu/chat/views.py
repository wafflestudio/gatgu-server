from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chat.models import OrderChat, ChatMessages, ParticipantProfile
from django.contrib.auth.models import User
# Create your views here.

# /chat/<int:chat_id>/
@csrf_exempt
def chat(request, chat_id):
    if request.method == 'GET':
        chat = OrderChat.objects.get(id=chat_id)
        participants = chat.participants
        response = {'chat_id': chat_id, 'article_id': article_id, 'participants': participants, 'order_status': chat.order_status, 'tracking_number': chat.tracking_number}
        return JsonResponse(response, safe=False, status=200)

# /chat/join/<int:chat_id>/
def join(request, chat_id):
    if request.method == 'PUT': # already in => success
        chat = OrderChat.objects.get(id=chat_id)
        response = {'status': 'success'}
        user = User.objects.get(id=request.user_id)

        if user in chat.participants:
            pass 
        elif chat.cur_people < chat.required_people: # can go in => success

            chat.cur_people += 1
            pass 
        else:
            response.status = 'failure' # full room => failure

        return JsonResponse(response, safe=False, status=200)

# /chat/out/<int:chat_id>/
def out(request, chat_id):
    if request.method == 'PUT':
        chat = OrderChat.objects.get(id=chat_id)
        response = {'status': 'success'}
        user = User.objects.get(id=request.user_id)

        if user not in chat.participants: # not in room
            response.status = 'failure'
        else: # room member is going out
            pass
        
        return JsonResponse(response, safe=False, status=200)
        
# /chat/<int:chat_id>/message/
def messages(request, chat_id):
    if request.method == 'GET':
        messages = [message for message in ChatMessage.objects.filter(chatroom_id==chat_id).values()]
        user = request.user
        joined_at = ParticipantProfile.objects.get(order_id==chat_id, participant_id==user.id)
        messages = messages.filter(joined_at<sent_at)
        
        return JsonResponse(messages, safe=False, status=200)
    elif request.method == 'POST':
        
# /chat/message/<int:message_id>/
def message(request, message_id):
    if request.method == 'GET':
# /chat/<int:chat_id>/participants/
def participants(request, chat_id):
    pass
