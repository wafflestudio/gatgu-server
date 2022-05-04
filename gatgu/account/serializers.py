from rest_framework import serializers

from account.models import Person


class PersonSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Person
        fields = (
            "id",
            "email",
            "password",
            "nickname",
            "date_joined",
        )
