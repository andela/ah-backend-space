import re

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.CharField(
        max_length=128,
        write_only=True
    )

    email = serializers.EmailField()
    username = serializers.CharField()
    auth_token = serializers.CharField(max_length=255, read_only=True)

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password', 'auth_token']

    @classmethod
    def validate_password(cls, password):
        # password to be of reasonable length, alphanumeric

        if len(password) < 8:
            raise serializers.ValidationError(
                "Password must be longer than 8 characters.")
        elif re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)", password) is None:
            raise serializers.ValidationError(
                "Password should at least contain a number, capital and small letter.")
        return password

    @classmethod
    def validate_email(cls, email):
        # we check that the same email is not registered more than once

        check_email = User.objects.filter(email=email)
        if check_email.exists():
            raise serializers.ValidationError("Email already exists.")
        return email

    @classmethod
    def validate_username(cls, username):
        # we check that the same username is not registered more than once
        check_username = User.objects.filter(username=username)
        if check_username.exists():
            raise serializers.ValidationError("Username already exists.")
        elif re.match(r"^([a-zA-Z\d]+[-_])*[a-zA-Z\d*]+$", username) is None:
            raise serializers.ValidationError(
                "username cannot be integers, have white spaces or symbols.")

        return username

    @classmethod
    def create(cls, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    auth_token = serializers.CharField(max_length=225, read_only=True)

    @classmethod
    def validate(cls, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )
        # This flag is raised when a user attempts to login without verifying
        # their accounts
        if not user.is_valid:
            raise serializers.ValidationError(
                'This user has not been verified, please check your email to verify.'
            )

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'auth_token': user.auth_token,
        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'auth_token')

        read_only_feilds = ('auth_token',)

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.

    @classmethod
    def update(cls, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance


class ResetEmailSerializer(serializers.ModelSerializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    @classmethod
    def validate_email(cls, value):
        try:
            valid_email = User.objects.get(email=value)
        except Exception:
            raise serializers.ValidationError(f"{value} is Invalid")
        return value

    class Meta:
        model = User
        fields = ['email']


class PasswordResetSerializer(serializers.ModelSerializer):
    """
    Serializer for requesting password reset detail.
    """

    password1 = serializers.CharField(
        max_length=128,
        min_length=8,
        required=True,
        write_only=True,
        style={'input_type': 'password'})
    password2 = serializers.CharField(
        max_length=128,
        min_length=8,
        required=True,
        write_only=True,
        style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['password1', 'password2']
