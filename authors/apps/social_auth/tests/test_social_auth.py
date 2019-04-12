import json
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from authors.apps.authentication.models import User

from ..login_register import login_or_register_social_user
from .test_data import (invalid_facebook_token,
                        valid_facebook_token, valid_google_token,
                        valid_user)


class SocialAuthenticationTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_facebook_login_using_invalid_access_token(self):
        response = self.client.post(
            '/api/social-auth/facebook',
            {"user": invalid_facebook_token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('facebook.GraphAPI.get_object')
    def test_facebook_social_login_with_valid_access_token(self, facebook_user):

        facebook_user.return_value = {
            "email": "space@gmail.com",
            "name": "Space"
        }
        response = self.client.post(
            '/api/social-auth/facebook',
            json.dumps(valid_facebook_token),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_social_login_using_valid_tokens(self, google_user):
        google_user.return_value = {
            "email": "space@gmail.com",
            "name": "Space"
        }
        response = self.client.post(
            '/api/social-auth/google',
            json.dumps(valid_google_token),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_social_login_on_existing_social_user_with_valid_data(self):
        user = User.objects.create_user(**valid_user)
        user.is_active = True
        user.save()
        returned_social_user_data = {
            "email": "space@gmail.com",
            "name": "Space"
        }
        response = login_or_register_social_user(returned_social_user_data)
        self.assertIsInstance(response, dict)
        self.assertIn("token", response)
