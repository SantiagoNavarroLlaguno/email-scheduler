from rest_framework import serializers
from .models import CustomUser, Email, ContactList, Folder


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile_picture",
        ]


class EmailSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    recipient = UserSerializer()

    class Meta:
        model = Email
        fields = "__all__"


class ContactListSerializer(serializers.ModelSerializer):
    contacts = UserSerializer(many=True)

    class Meta:
        model = ContactList
        fields = "__all__"


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = "__all__"
