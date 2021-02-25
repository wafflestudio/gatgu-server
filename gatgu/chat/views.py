from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chat.models import OrderChat, ChatMessage, ParticipantProfile
from django.contrib.auth.models import User
import json
# Create your views here.

# /chat/
def chats(request):
    if request.method == 'GET': # needs : list of chatting overview(recent message, sender, send_at, article_title)
        user = request.user
        # find which chats this user participated
        chat_in = [chat for chat in ParticipantProfile.objects.filter(participant=user).values('chat')]
        chats = []
        #print(chat_in)
        for chat_id in chat_in:
            chat = list(OrderChat.objects.filter(id=chat_id['chat']).values('id', 'messages'))
            #recent message
            msgs = []
            for msg in chat:
                message = ChatMessage.objects.get(id=msg['messages'])
                msgs.append({'chat_id': msg['id'], 'recent_message': message.text, 'sent_by': message.sent_by.id, 'sent_at': message.sent_at})
            chats.append(msgs)
        print(chats)
        return JsonResponse({'chats': chats}, safe=False, status=200)

    else:
        return HttpResponseNotAllowed(['GET'])
        
# /chat/<int:chat_id>/
def chat(request, chat_id):
    if request.method == 'GET': # needs: messages, participants
        print(chat_id)
        chat = list(OrderChat.objects.filter(id=chat_id).values('messages'))
        msgs = []
        for msg in chat:
            message = ChatMessage.objects.get(id=msg['messages'])
            msgs.append({'chat_id': message.id, 'recent_message': message.text, 'sent_by': message.sent_by.id, 'sent_at': message.sent_at})
        print(msgs)
        return JsonResponse({'messages': msgs}, safe=False, status=200)
    else:
        return HttpResponseNotAllowed(['GET'])

# /chat/<int:chat_id>/join/
@csrf_exempt
def join(request, chat_id):
    if request.method == 'PUT': # already in => success
        participants = [part['participants'] for part in OrderChat.objects.filter(id=chat_id).values('participants')]
        user_id = request.user.id

        if user_id in participants:
            return HttpResponse(status=200)
        elif chat.cur_people < chat.required_people: # can go in => success
            # participant 추가
            new_participant = ParticipantProfile(chat=chat, participant=user)
            new_participant.save()
            chat.cur_people += 1
            chat.save()
            return HttpResponse(status=200)
        else:
             # full room => failure
             return HttpResponse(status=401)
    else:
        return HttpResponseNotAllowed(['PUT'])

# /chat/out/<int:chat_id>/
@csrf_exempt
def out(request, chat_id):
    if request.method == 'PUT':

        participants = [part['participants'] for part in OrderChat.objects.filter(id=chat_id).values('participants')]
        user_id = request.user.id

        if user_id not in participants: # not in room
            return HttpResponse(status=401)
        else: # room member is going out
            return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(['PUT'])
        
# /chat/<int:chat_id>/messages/
@csrf_exempt
def messages(request, chat_id):
    if request.method == 'GET':
        
        user = request.user
        messages = [message for message in ChatMessage.objects.filter(chatroom_id==chat_id).values('messages')]

        # joined_at = ParticipantProfile.objects.get(order_id==chat_id, participant_id==user.id)
        # messages = messages.filter(joined_at<sent_at) if you need after joined messages
        
        return JsonResponse(messages, safe=False, status=200)

    elif request.method == 'POST':
        body = json.loads(request.body.decode())
        msg_text = body["text"]
        msg_img = body["image_url"]
        #sent_at = datetime.datetime.now()
        chat = OrderChat.objects.get(id=chat_id)
        new_message = ChatMessage(text=msg_text, media=msg_img, sent_by=request.user, chat=chat)
        new_message.save()

        response = {"message_id": new_message.id}
        return JsonResponse(response, safe=False, status=200)
    
    return HttpResponseNotAllowed(['GET', 'POST'])

# /chat/message/<int:message_id>/
def message(request, message_id):
    if request.method == 'GET':
        message = ChatMessage.objects.filter(id=message_id).values()[0]
        print(message)
        return JsonResponse({'text': message['text'], 'media': message['media'], 'sent_by_id': message['sent_by_id'], 'sent_at': message['sent_at'], 'chat_id': message['chat_id'], 'type': message['type']}, safe=False, status=200)
    else:
        return HttpResponseNotAllowed(['GET'])

# /chat/<int:chat_id>/participants/
def participants(request, chat_id):
    if request.method == 'GET':
        print(13)
        participants = ParticipantProfile.objects.filter(participant_id=chat_id).values()[0]
        print(participants)     
        return JsonResponse(participants, safe=False, status=200)
    else:
        return HttpResponseNotAllowed(['GET'])

# /chat/<int:chat_id>/set_status/
def set_status(request, chat_id):
    if request.method == 'PUT':
        body = json.loads(request.body.decode())
        new_status = body["status"]
        chat = OrderChat.objects.get(id=chat_id)
        chat.order_status = new_status
        chat.save()

        response = body
        return JsonResponse(response, safe=False, status=200)
    
    else:
        return HttpResponseNotAllowed(['GET', 'PUT'])