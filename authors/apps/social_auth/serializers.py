from rest_framework import serializers


class SocialAuthSerializer(serializers.Serializer):

    access_token = serializers.CharField(min_length=10)
