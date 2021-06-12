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
from chat.models import OrderChat, ChatMessage, ParticipantProfile
from chat.serializers import OrderChatSerializer, ChatMessageSerializer, ParticipantProfileSerializer, \
    SimpleOrderChatSerializer
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

    #
    # def list(self, request):  # get: /chat/
    #     user = request.user
    #     if user is None or not user.is_active:
    #         return Response('message: 탈퇴하거나 없는 회원입니다.', status=status.HTTP_403_FORBIDDEN)
    #     queryset = User.objects.get(id=user.id).order_chat
    #     serializer = SimpleOrderChatSerializer(queryset, many=True)
    #     return Response(serializer.data)

    # get one chat
    def retrieve(self, request, pk=None):  # get: /chat/{chat_id}/
        order_chat = get_object_or_404(OrderChat, pk=pk)
        return Response(OrderChatSerializer(order_chat).data)

    # join a chat
    @action(detail=True, methods=['PUT'])
    def join(self, request, pk=None):
        user_id = request.user.id
        article = get_object_or_404(Article, pk=pk)
        if article.writer_id == user_id:
            return Response(status=status.HTTP_200_OK)
        elif pk in self.chat_list(user_id):
            return Response(status=status.HTTP_200_OK)
        else:
            participant = ParticipantProfile(order_chat_id=pk, participant_id=user_id)
            participant.save()
            return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['PUT'])
    def out(self, request, pk=None):
        user_id = request.user.id
        if pk in self.chat_list(user_id):
            participant = ParticipantProfile.objects.get(order_chat_id=pk, participant_id=user_id)
            participant.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

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

            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['GET'])
    def participants(self, request, pk=None):
        chat = get_object_or_404(OrderChat, pk=pk)
        participants = chat.participant_profile
        return Response(ParticipantProfileSerializer(participants, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'])
    def set_status(self, request, pk=None):
        user = request.user
        data = request.data
        new_status = data['order_status']
        chat = get_object_or_404(OrderChat, pk=pk)
        if chat.article.writer_id == user.id:
            chat.order_status = new_status
            chat.save()
            return Response(self.get_serializer(chat).data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['PUT'], serializer_class=ParticipantProfileSerializer)
    def set_wish_price(self, request, pk=None):
        user = request.user
        data = request.data
        new_price = data['wish_price']
        # chat = get_object_or_404(OrderChat, pk=pk)

        if pk in self.chat_list(user.id):
            participant = get_object_or_404(ParticipantProfile, participant_id=user.id, order_chat_id=pk)
            participant.wish_price = new_price
            participant.save()

            # sum_wish_price = Coalesce(Subquery(
            #     ParticipantProfile.objects.filter(order_chat_id=pk).annotate(
            #         sum=Sum('wish_price')).values('sum'), output_field=IntegerField()), 0)
            chat = OrderChat.objects.annotate(sum_wish_price=Sum('participant_profile__wish_price')).get(id=pk)

            serializer = self.get_serializer(chat, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.update(chat, serializer.validated_data)

            if chat.sum_wish_price >= chat.article.price_min:
                chat.article.article_status = 2

            else:
                chat.article.article_status = 1

            serializer.save()

            data = ParticipantProfileSerializer(participant).data
            data['article_status'] = chat.article.article_status

            return Response(data, status=status.HTTP_200_OK)
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
    def set_tracking_number(self, request, pk=None):
        user = request.user
        data = request.data
        new_tracking_number = data['tracking_number']
        chat = get_object_or_404(OrderChat, pk=pk)
        if chat.article.writer_id == user.id:
            chat.tracking_number = new_tracking_number
            chat.save()
            return Response(self.get_serializer(chat).data, status=status.HTTP_200_OK)
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
