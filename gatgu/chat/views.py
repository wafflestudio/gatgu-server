from django.db import transaction
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action
from rest_framework.pagination import CursorPagination, PageNumberPagination

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from rest_framework.utils import json

from article.models import Article
from chat.models import OrderChat, ChatMessage, ParticipantProfile
from chat.serializers import OrderChatSerializer, ChatMessageSerializer, ParticipantProfileSerializer, \
    SimpleOrderChatSerializer


# /chat/
def chats(request):
    if request.method == 'GET':  # needs : list of chatting overview(recent message, sender, send_at, article_title)
        user = request.user
        if user.is_anonymous:
            return HttpResponse(status=401)
        # find which chats this user participated
        chat_in = [chat['order_chat'] for chat in
                   ParticipantProfile.objects.filter(participant=user).values('order_chat')]

        chats = []
        # print(chat_in)
        for chat_id in chat_in:
            chat = list(OrderChat.objects.filter(id=chat_id).values('id', 'messages'))

            # if len(chat)>0:
            print(chat)

            message_id = chat[-1]['messages']

            print(message_id)
            # else:
            #    continue
            try:
                message = ChatMessage.objects.get(id=message_id)
            except:
                chats.append({'chat_id': chat_id, 'recent_message': None, 'sent_by_id': None, 'sent_at': None})
                continue
                # recent message
            print(chat_id)
            msg = {'chat_id': chat_id, 'recent_message': {'text': message.text, 'media': message.media},
                   'sent_by_id': message.sent_by.id, 'sent_at': message.sent_at}
            chats.append(msg)
        print(chats)
        return JsonResponse({'chats': chats}, safe=False, status=200)

    def chat_list(self, user_id):
        participants = [str(participant['order_chat_id']) for participant in
                        ParticipantProfile.objects.filter(participant_id=user_id).values('order_chat_id')]
        return participants

    def list(self, request):  # get: /chat/
        user = request.user
        if user is None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        queryset = User.objects.get(id=user.id).order_chat
        serializer = SimpleOrderChatSerializer(queryset, many=True)
        return Response(serializer.data)

    # get one chat
    def retrieve(self, request, pk=None):  # get: /chat/{chat_id}/
        order_chat = get_object_or_404(OrderChat, pk=pk)
        return Response(OrderChatSerializer(order_chat).data)

    # join a chat
    @action(detail=True, methods=['PUT'])
    def join(self, request, pk=None):
        user_id = request.user.id
        chat = OrderChat.objects.get(id=chat_id)
        if user_id in participants:
            return HttpResponse(status=200)
        elif chat.order_status == 1:  # can go in => success =========> order_status에 따른 것으로 변경
            # participant 추가
            new_participant = ParticipantProfile(order_chat_id=chat.id, participant=request.user)

            print(new_participant)
            new_participant.save()
            # chat.cur_people += 1

            chat.save()
            return HttpResponse(status=200)
        else:
            participant = ParticipantProfile(order_chat_id=pk, participant_id=user_id)
            participant.save()
            return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['PUT'])
    def out(self, request, pk=None):
        user_id = request.user.id
        if user_id not in participants:  # not in room
            return HttpResponse(status=403)
        else:  # room member is going out
            profile = ParticipantProfile.objects.get(order_chat_id=chat_id, participant_id=user_id)
            profile.save()

            # chat = OrderChat.objects.get(id=chat_id)
            # chat.save()

            return HttpResponse(status=200)

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
            # message = ChatMessage.objects.get(id=msg['messages'])
            user_profile = User.objects.get(id=message['sent_by_id']).userprofile
            msgs.append({'id': message['id'], 'text': message['text'], 'media': message['media'],
                         'user': {'user_id': message['sent_by_id'], 'nickname': user_profile.nickname,
                                  'profile': user_profile.picture.url}, 'sent_at': message['sent_at']})
        # joined_at = ParticipantProfile.objects.get(order_id==chat_id, participant_id==user.id)
        # messages = messages.filter(joined_at<sent_at) if you need after joined messages

        return JsonResponse(msgs, safe=False, status=200)


    elif request.method == 'POST':
        body = json.loads(request.body.decode())
        msg_text = body["text"]
        msg_img = body["media"]

        if request.user.is_anonymous:
            return HttpResponse(status=401)
        # sent_at = datetime.datetime.now()
        try:
            chat = OrderChat.objects.get(id=chat_id)
        except Exception as e:
            return HttpResponse(status=404)
        participants = [participant['participant_id'] for participant in
                        ParticipantProfile.objects.filter(order_chat_id=chat_id).values('participant_id')]

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
        return JsonResponse({'id': message['id'], 'text': message['text'], 'media': message['media'],
                             'user': {'user_id': message['sent_by_id'], 'nickname': user_profile.nickname,
                                      'profile': user_profile.picture.url}, 'sent_at': message['sent_at'],
                             'chat_id': message['chat_id'], 'type': message['type']}, safe=False, status=200)

    else:
        return HttpResponseNotAllowed(['GET'])


# /chat/<int:chat_id>/participants/
@csrf_exempt
def participants(request, chat_id):
    if request.method == 'GET':
        if request.user.is_anonymous:
            return HttpResponse(status=401)
        participants = [participant for participant in
                        ParticipantProfile.objects.filter(order_chat_id=chat_id).values('participant_id', 'joined_at',
                                                                                        'pay_status', 'wish_price')]

        '''res = []
        for participant_id in participants:
            person = ParticipantProfile.objects.get(order_chat_id=)'''
        # participants = ParticipantProfile.objects.filter(participant_id=chat_id).values()[0]

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

        participants = [participant['participant_id'] for participant in
                        ParticipantProfile.objects.filter(order_chat_id=chat_id).values('participant_id')]

        if not request.user.id in participants:
            return HttpResponse(status=403)

        body = json.loads(request.body.decode())
        new_amount = body['amount']
        participant = ParticipantProfile.objects.get(order_chat_id=chat_id, participant_id=request.user.id)
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
        participants = participants = [participant['participant_id'] for participant in
                                       ParticipantProfile.objects.filter(order_chat_id=chat_id).values(
                                           'participant_id')]

        if not body['user_id'] in participants:
            return HttpResponse(status=403)

        participant = ParticipantProfile.objects.get(order_chat_id=chat_id, participant_id=body['user_id'])

        participant.pay_status = True
        participant.save()
        return HttpResponse(status=200)

    def get_permissions(self):
        return self.permission_classes


@csrf_exempt
def set_tracking(request, chat_id):
    if request.method == 'PUT':
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
        chat['tracking_number'] = body['tracking_number']
        chat.save()
        return HttpResponse(status=200)

    else:
        return HttpResponseNotAllowed(['PUT'])
