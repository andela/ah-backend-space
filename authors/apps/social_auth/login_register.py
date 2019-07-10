import uuid
from django.core.exceptions import ValidationError

from authors.apps.authentication.models import User


def login_or_register_social_user(social_user):
    try:
        user = User.objects.get(email=social_user.get('email'))
    except User.DoesNotExist:
        if social_user.get("email") is None:
            raise ValidationError("Users must have an email address.")

        anonymous_user = str(uuid.uuid4())
        new_social_user = {
            "email": social_user.get("email"),
            "username": social_user.get("name", anonymous_user),
            "password": User.objects.make_random_password()
        }

        user = User.objects.create_user(**new_social_user)
        user.is_active = True
        user.save()

    return {
            "email": social_user.get("email"),
            "username": social_user.get("name"),
            "token": user.auth_token()
            }
