import os

import facebook
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from authors.apps.social_auth.serializers import SocialAuthSerializer
from authors.apps.authentication.renderers import UserJSONRenderer


from .exceptions import SocialAuthenticationFailed
from .login_register import login_or_register_social_user


class FacebookAuthAPIView(CreateAPIView):
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SocialAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = dict(serializer.validated_data)["access_token"]

        try:
            graph = facebook.GraphAPI(access_token=access_token)
            facebook_user = graph.get_object(id='me', fields='email, name')
        except:
            raise SocialAuthenticationFailed
        response = login_or_register_social_user(facebook_user)
        return Response(response, status=status.HTTP_200_OK)


class GoogleAuthAPIView(CreateAPIView):
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SocialAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = dict(serializer.validated_data)["access_token"]
        try:
            google_user = id_token.verify_oauth2_token(
                access_token, requests.Request())
        except:
            raise SocialAuthenticationFailed
        response = login_or_register_social_user(google_user)
        return Response(response, status=status.HTTP_200_OK)
