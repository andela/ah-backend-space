from rest_framework.exceptions import APIException


class SocialAuthenticationFailed(APIException):
    status_code = 400
    default_detail = "Social Authentication Failed, Token expired or invalid"
