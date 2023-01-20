from django.contrib.auth import get_user_model
from rest_framework import serializers


class GarpixCompanyUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'email')
