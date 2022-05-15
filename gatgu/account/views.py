from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from account.models import Person
from account.serializers import PersonSerializer


class PersonViewSet(viewsets.GenericViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticated(),)

    def get_permissions(self):
        # if self.action in ("create", "login"):
        return (AllowAny(),)
        # return self.permission_classes

    def create(self, request):
        data = request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        person = Person(
            email=data.get("email"),
            nickname=data.get("nickname"),
            password=make_password(data.get("password")),
        )
        person.save()
        return Response(
            self.get_serializer(person).data, status=status.HTTP_201_CREATED
        )

    def list(self, request):
        persons = self.get_queryset()
        serializer = self.get_serializer(persons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["PUT"])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response(
                {"error": "Wrong Email or Password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    def logout(self, request):
        logout(request)
        return Response(
            {"message": "Successfully Logged out"}, status=status.HTTP_200_OK
        )
