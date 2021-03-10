from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action
from rest_framework.pagination import CursorPagination, PageNumberPagination

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from chat.models import OrderChat, ChatMessage, ParticipantProfile
from chat.serializers import OrderChatSerializer, ChatMessageSerializer, ParticipantProfileSerializer

class OrderChatViewSet(viewsets.GenericViewSet):
    queryset = OrderChat.objects.all()
    serializer_class = OrderChatSerializer
    permission_classes = (IsAuthenticated(),)
    
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
    def list(self, request): # get: /chat/
        user = request.user
        if user is None:
            return Response(status=status.HTTP_403_FORBIDDEN)
        queryset = User.objects.get(id=user.id).order_chat
        serializer = OrderChatSerializer(queryset, many=True)
        return Response(serializer.data)

    # get one chat
    def retrieve(self, request, pk=None): # get: /chat/{chat_id}/
        order_chat = get_object_or_404(OrderChat, pk=pk)
        return Response(self.get_serializer(order_chat).data)
    
    # join a chat
    @action(detail=True, methods=['PUT'])
    def join(self, request, pk=None):
        print(request.user.participant_profile)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['PUT'])
    def out(self, request, pk=None):
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET', 'POST'])
    def messages(self, request, pk=None):
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'])
    def participants(self, request, pk=None):
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PUT'])
    def set_status(self, request, pk=None):
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PUT'])
    def set_buy_amount(self, request, pk=None):
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PUT'])
    def pain(self, request, pk=None):
        return Response(status=status.HTTP_200_OK)

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
