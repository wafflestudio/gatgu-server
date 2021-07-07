from django.db.models.functions import Coalesce
from django.db.models import Prefetch, Subquery, OuterRef, Count, IntegerField, Sum, F

from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action
from rest_framework.pagination import CursorPagination, PageNumberPagination

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication

from article.models import Article
from article.serializers import ArticleSerializer
from chat.models import OrderChat, ChatMessage, ParticipantProfile, ChatMessageImage
from chat.serializers import OrderChatSerializer, ChatMessageSerializer, ParticipantProfileSerializer, \
    SimpleOrderChatSerializer, ChatMessageImageSerializer
from gatgu.paginations import CursorSetPagination

import boto3
from botocore.client import Config


class CursorSetPagination(CursorSetPagination):
    ordering = '-sent_at'


class OrderChatViewSet(viewsets.GenericViewSet):
    queryset = OrderChat.objects.all()
    serializer_class = OrderChatSerializer
    permission_classes = (IsAuthenticated(),)
    pagination_class = CursorSetPagination
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        return self.permission_classes

    '''@transaction.atomic
    def create(self, request):
        user = request.user
        data = request.data

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()'''

    # list of chat user is in

    def chat_list(self, user_id):
        participants = [str(participant['order_chat_id']) for participant in
                        ParticipantProfile.objects.filter(participant_id=user_id).values('order_chat_id')]
        return participants

    # get one chat
    def retrieve(self, request, pk):
        """
        GET v1/chattings/{chatting_id}/
        """
        order_chat = get_object_or_404(OrderChat, pk=pk)
        return Response(OrderChatSerializer(order_chat).data)

    @action(methods=['GET', 'POST', 'PATCH', 'DELETE'], detail=True)
    def participants(self, request, pk):
        """
        join or out a chat, participant list
        GET v1/chattings/{chatting_id}/participants/
        POST v1/chattings/{chatting_id}/participants/
        PATCH v1/chattings/{chatting_id}/participants/
        DELETE v1/chattings/{chatting_id}/participants/

        [data params]
        if method == PATCH
            wish_price

        """
        user = request.user
        try:
            chatting = OrderChat.objects.select_related('article').get(id=pk)
        except OrderChat.DoesNotExist:
            return Response({"없쪙"}, status=status.HTTP_404_NOT_FOUND)

        if request.method == "GET":
            participant_profiles = chatting.participant_profile
            return Response(ParticipantProfileSerializer(participant_profiles, many=True).data,
                            status=status.HTTP_200_OK)

        elif request.method == 'POST':
            # article 의 status 가 모집중 이 아니면 입장 불가.
            if chatting.article.article_status != Article.GATHERING:
                return Response({"Could not participate"}, status=status.HTTP_404_NOT_FOUND)

            if chatting.article.writer == user:
                return Response(status=status.HTTP_200_OK)
            elif OrderChat.objects.filter(participant_profile__participant=user).exists():
                return Response(status=status.HTTP_200_OK)
            elif chatting.order_status == 1:
                ParticipantProfile.objects.create(order_chat=chatting, participant=user)
                return Response(status=status.HTTP_201_CREATED)
            else:
                # full chatting room
                return Response(status=status.HTTP_403_FORBIDDEN)

        elif request.method == 'PATCH':
            """
            PATCH v1/chattings/{chatting_id}/participants/
            로그인한 유저가 {chatting_id} 방의 본인의 participant 정보를 수정.
            [수정 가능 필드]
            - wish_price
            
            [todo]
            - pay_status 로직:
                1. 로그인 한 유저가 수정 요청을 채팅방장에게 send 
                2. 방장이 approve
                3. pay_status update.
            -> 채팅방에서 방장에게 메세지 형식으로 보내는 방법 고려해보기.
            """
            # 1. 해당 채팅방의 참가자인지 validate
            try:
                participant_profile = ParticipantProfile.objects.get(order_chat=chatting, participant=user)
            except ParticipantProfile.DoesNotExist:
                return Response({'채팅방에 참여하고 있지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

            wish_price = request.data.get('wish_price')
            if type(wish_price) != int:
                return Response({'invalid wish_price'}, status=status.HTTP_400_BAD_REQUEST)

            participant_profile.wish_price = wish_price
            participant_profile.save()
            return Response(status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            # 참가자의 요청시 나가기 처리
            # 방장의 요청시
            #   1. 본인 나가기 불가
            #   2. data param 있을때(추방가능한 유저의 아이디 인지 validate)
            if chatting.article.writer == user:
                exile_id = request.data.get('user_id')
                if exile_id not in chatting.participant_profile.participant.id:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                exile_id = user.id

            try:
                participant = ParticipantProfile.objects.get(order_chat=chatting, participant_id=exile_id)
                participant.delete()
                return Response(status=status.HTTP_200_OK)
            except ParticipantProfile.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET', 'POST'], serializer_class=ChatMessageSerializer)
    def messages(self, request, pk=None):
        if request.method == 'GET':
            chat = get_object_or_404(OrderChat, pk=pk)
            messages = chat.messages
            # messages = ChatMessage.objects.filter(chat__article_id=pk)

            page = self.paginate_queryset(messages)
            assert page is not None
            serializer = ChatMessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        elif request.method == 'POST':
            data = request.data
            user = request.user
            serializer = ChatMessageSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(sent_by=user, chat_id=pk)
            message_id = ChatMessage.objects.last().id
            message = ChatMessage.objects.get(id=message_id)

            if 'image' in data and data['image'] != '':
                message.image.create(img_url=data['image'])
                message.save()

            message = ChatMessage.objects.get(id=message_id)
            img = message.image.all()[0]
            ser = ChatMessageImageSerializer(img)
            print(ser.data)
            print(message.image.values())

            return Response(ChatMessageSerializer(message).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk):
        """
        writer 가 채팅방의 order_status, tracking_number 를 수정
        동시에 수정 불가.
        """
        try:
            chatting = OrderChat.objects.filter(id=pk).select_related('article').get()
        except OrderChat.DoesNotExist:
            return Response('not found')

        # could update only writer
        if chatting.article.writer != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        order_status = request.data.get('order_status')
        tracking_number = request.data.get('tracking_number')

        # could not update (both at once or nothing)
        if (order_status is not None and tracking_number is not None) or (
                order_status is None and tracking_number is None):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if order_status is not None:
            # validate (order_status's range 1 ~ 4)
            if order_status not in [i for i, s in OrderChat.ORDER_STATUS]:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                chatting.order_status = order_status

        elif tracking_number is not None:
            chatting.tracking_number = tracking_number

        chatting.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], serializer_class=ParticipantProfileSerializer)
    def paid(self, request, pk=None):
        user = request.user
        data = request.data
        target_user_id = data['user_id']
        chat = get_object_or_404(OrderChat, pk=pk)
        if chat.article.writer_id == user.id and pk in self.chat_list(target_user_id):
            participant = ParticipantProfile.objects.get(order_chat_id=pk, participant_id=target_user_id)
            participant.pay_status = True
            participant.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['PUT'])
    def get_presigned_url(self, request, pk=None):
        user = request.user
        data = request.data
        if data['method'] == 'get' or data['method'] == 'GET':
            s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='ap-northeast-2'))
            url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': 'gatgubucket',
                    'Key': data['file_name']
                },
                ExpiresIn=3600,
                HttpMethod='GET')
            return Response({'presigned_url': url, 'file_name': data['file_name']}, status=status.HTTP_200_OK)
        elif data['method'] == 'put' or data['method'] == 'PUT':
            s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='ap-northeast-2'))
            url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': 'gatgubucket',
                    'Key': 'chat/{0}/{1}_{2}'.format(pk, data['file_name'], user.id)
                },
                ExpiresIn=3600,
                HttpMethod='PUT')
            return Response(
                {'presigned_url': url, 'file_name': 'chat/{0}/{1}_{2}'.format(pk, data['file_name'], user.id)},
                status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class ChatMessageViewSet(viewsets.GenericViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        return self.permission_classes

    def list(self, request):
        user = request.user
        if user is None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        queryset = User.objects.get(id=user.id).messages
        serializer = ChatMessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        message = get_object_or_404(ChatMessage, pk=pk)
        return Response(self.get_serializer(message).data)
