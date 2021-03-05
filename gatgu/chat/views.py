from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chat.models import OrderChat, ChatMessage, ParticipantProfile
from django.contrib.auth.models import User
import json
import datetime
# Create your views here.

# /chat/
def chats(request):
    if request.method == 'GET': # needs : list of chatting overview(recent message, sender, send_at, article_title)
        user = request.user
        if user.is_anonymous: 
            return HttpResponse(status=401)
        # find which chats this user participated


        chat_in = [chat for chat in ParticipantProfile.objects.filter(participant=user).values('order_chat')]
        chats = []
        #print(chat_in)
        for chat_id in chat_in:
            chat = list(OrderChat.objects.filter(id=chat_id['order_chat']).values('id', 'messages'))
            if len(chat)>0:
                message_id = chat[-1]['messages']
            else:
                continue
            message = ChatMessage.objects.get(id=message_id)
            #recent message
            msg = {'chat_id': chat_id, 'recent_message':{'text': message.text, 'media': message.media}, 'sent_by_id': message.sent_by.id, 'sent_at': message.sent_at}
            chats.append(msg)
        print(chats)
        return JsonResponse({'chats': chats}, safe=False, status=200)

    else:
        return HttpResponseNotAllowed(['GET'])
        
# /chat/<int:chat_id>/
def chat(request, chat_id):
    if request.method == 'GET': # needs: messages, participants
        if request.user.is_anonymous:
            return HttpResponse(status=401)
        try:
            chat = OrderChat.objects.get(id=chat_id)
        except Exception as e:
            return HttpResponse(status=404)
        msgs = []
        messages = list(chat.messages.all().values())
        for message in messages:
            #message = ChatMessage.objects.get(id=msg['messages'])
            msgs.append({'id': message['id'], 'text': message['text'], 'media': message['media'], 'sent_by_id': message['sent_by_id'], 'sent_at': message['sent_at']})
        chat_info = {
            'order_status': chat.order_status,
            'tracking_number': chat.tracking_number,


            'required_people': chat.article.people_min,
            #'cur_people': chat.article.cur_people,
            'participants_id': [id['id'] for id in chat.participants.all().values('id')],
            'article_id': chat.article_id,
            #'messages': msgs
        }
        print(chat_info)
        return JsonResponse({'messages': chat_info}, safe=False, status=200)
    else:
        return HttpResponseNotAllowed(['GET'])

# /chat/<int:chat_id>/join/
@csrf_exempt
def join(request, chat_id):
    if request.method == 'PUT': # already in => success


        #participants = [part['participants'] for part in OrderChat.objects.filter(id=chat_id).values('participants')]
        participants = [participant['participant_id'] for participant in ParticipantProfile.objects.filter(order_chat_id=chat_id, out_at=None).values('participant_id')]
        if request.user.is_anonymous:
            return HttpResponse(status=401)
        user_id = request.user.id
        chat = OrderChat.objects.get(id=chat_id)
        if user_id in participants:
            return HttpResponse(status=200)
        elif chat.order_status==1: # can go in => success =========> order_status에 따른 것으로 변경
            # participant 추가
            new_participant = ParticipantProfile(order_chat=chat, participant=request.user)
            print(new_participant)
            new_participant.save()
            #chat.cur_people += 1
            chat.save()
            return HttpResponse(status=200)
        else:
             # full room => failure
             return HttpResponse(status=403)
    else:
        return HttpResponseNotAllowed(['PUT'])

# /chat/out/<int:chat_id>/
@csrf_exempt
def out(request, chat_id):
    if request.method == 'PUT':
        try:


            print(ParticipantProfile.objects.all())
            participants = [participant['participant_id'] for participant in ParticipantProfile.objects.filter(order_chat_id=chat_id, out_at=None).values('participant_id')]
        except Exception as e:
            return HttpResponse(status=404)
        if request.user.is_anonymous:
            return HttpResponse(status=401)
        user_id = request.user.id
        if user_id not in participants: # not in room
            return HttpResponse(status=403)
        else: # room member is going out


            profile = ParticipantProfile.objects.get(order_chat_id=chat_id, participant_id=user_id, out_at=None)
            profile.out_at=datetime.datetime.now()
            profile.save()
            #chat = OrderChat.objects.get(id=chat_id)
            #chat.save()
            return HttpResponse(status=200)
    else:
        return HttpResponseNotAllowed(['PUT'])
        
# /chat/<int:chat_id>/messages/
@csrf_exempt
def messages(request, chat_id):
    if request.method == 'GET':


        if request.user.is_anonymous:
            return HttpResponse(status=401)
        try:
            chat = OrderChat.objects.get(id=chat_id)
        except Exception as e:
            return HttpResponse(status=404)
        msgs = []
        messages = list(chat.messages.all().values())
        for message in messages:
            #message = ChatMessage.objects.get(id=msg['messages'])
            user_profile = User.objects.get(id=message['sent_by_id']).userprofile
            msgs.append({'id': message['id'], 'text': message['text'], 'media': message['media'], 'user': {'user_id': message['sent_by_id'], 'nickname': user_profile.nickname, 'profile': user_profile.picture.url}, 'sent_at': message['sent_at']})
        # joined_at = ParticipantProfile.objects.get(order_id==chat_id, participant_id==user.id)
        # messages = messages.filter(joined_at<sent_at) if you need after joined messages
        
        return JsonResponse(msgs, safe=False, status=200)

    elif request.method == 'POST':
        body = json.loads(request.body.decode())
        msg_text = body["text"]


        msg_img = body["media"]
        if request.user.is_anonymous:
            return HttpResponse(status=401)
        #sent_at = datetime.datetime.now()
        try:
            chat = OrderChat.objects.get(id=chat_id)
        except Exception as e:
            return HttpResponse(status=404)


        participants = [participant['participant_id'] for participant in ParticipantProfile.objects.filter(order_chat_id=chat_id, out_at=None).values('participant_id')]

        if request.user.id not in participants:
            return HttpResponse(status=403)
        new_message = ChatMessage(text=msg_text, media=msg_img, sent_by=request.user, chat=chat)
        new_message.save()

        response = {"message_id": new_message.id}
        return JsonResponse(response, safe=False, status=200)
    
    return HttpResponseNotAllowed(['GET', 'POST'])

# /chat/message/<int:message_id>/
def message(request, message_id):
    if request.method == 'GET':
        if request.user.is_anonymous:
            return HttpResponse(status=401)
        message = ChatMessage.objects.filter(id=message_id).values()[0]
        print(message)


        user_profile = User.objects.get(id=message['sent_by_id']).userprofile
        return JsonResponse({'id': message['id'], 'text': message['text'], 'media': message['media'], 'user': {'user_id': message['sent_by_id'], 'nickname': user_profile.nickname, 'profile': user_profile.picture.url}, 'sent_at': message['sent_at'], 'chat_id': message['chat_id'], 'type': message['type']}, safe=False, status=200)
    else:
        return HttpResponseNotAllowed(['GET'])

# /chat/<int:chat_id>/participants/
def participants(request, chat_id):
    if request.method == 'GET':
        if request.user.is_anonymous:
            return HttpResponse(status=401)


        participants = [participant for participant in ParticipantProfile.objects.filter(order_chat_id=chat_id, out_at=None).values('participant_id', 'joined_at', 'pay_status', 'wish_price')]
        '''res = []
        for participant_id in participants:
            person = ParticipantProfile.objects.get(order_chat_id=)'''
        #participants = ParticipantProfile.objects.filter(participant_id=chat_id).values()[0]
        print(participants)     
        return JsonResponse(participants, safe=False, status=200)
    else:
        return HttpResponseNotAllowed(['GET'])

# /chat/<int:chat_id>/set_status/


@csrf_exempt
def set_status(request, chat_id):
    if request.method == 'PUT':
        if request.user.is_anonymous:
            return HttpResponse(status=401)
        body = json.loads(request.body.decode())
        new_status = body["status"]
        chat = OrderChat.objects.get(id=chat_id)
        chat.order_status = new_status
        chat.save()

        response = body
        return JsonResponse(response, safe=False, status=200)
    
    else:


        return HttpResponseNotAllowed(['GET', 'PUT'])

@csrf_exempt 
def set_buy_amount(request, chat_id):
    if request.method == 'PUT':
        if request.user.is_anonymous:
            return HttpResponse(status=401)

        participants = [participant['participant_id'] for participant in ParticipantProfile.objects.filter(order_chat_id=chat_id, out_at=None).values('participant_id')]
        if not request.user.id in participants:
            return HttpResponse(status=403)
        
        body = json.loads(request.body.decode())
        new_amount = body['amount']
        participant = ParticipantProfile.objects.get(order_chat_id=chat_id, participant_id=request.user.id, out_at=None)
        participant.wish_price = new_amount
        participant.save()

        response = body
        return JsonResponse(response, safe=False, status=200)
    
    else:
        return HttpResponseNotAllowed(['PUT'])

@csrf_exempt
def paid(request, chat_id):
    if request.method == 'PUT':
        print(request.user.id)
        if request.user.is_anonymous:
            return HttpResponse(status=401)
        
        try:
            chat = OrderChat.objects.get(id=chat_id)
        except Exception as e:
            return HttpResponse(status=404)

        if not request.user.id == chat.article.writer_id:
            print(request.user.id)
            print(chat.article.writer_id)
            return HttpResponse(status=403)

        body = json.loads(request.body.decode())
        participants = participants = [participant['participant_id'] for participant in ParticipantProfile.objects.filter(order_chat_id=chat_id, out_at=None).values('participant_id')]
        if not body['user_id'] in participants:
            return HttpResponse(status=403)
        
        participant = ParticipantProfile.objects.get(order_chat_id=chat_id, participant_id=body['user_id'], out_at=None)
        participant.pay_status = True
        participant.save()
        return HttpResponse(status=200)

    else:
        return HttpResponseNotAllowed(['PUT'])
