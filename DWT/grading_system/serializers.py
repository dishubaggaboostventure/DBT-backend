from django.db.models import Q  # for queries
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import *
from django.core.exceptions import ValidationError
from uuid import uuid4


class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(max_length=128)
    first_name = serializers.CharField(max_length=100, required=True, )
    last_name = serializers.CharField(max_length=100, required=True, )
    CATEGORY = (('pupil', 'pupil'), ('admin', 'admin'), ('teacher', 'teacher'))
    user_type = serializers.ChoiceField(choices=CATEGORY, required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'user_type'
        )


class UserLoginSerializer(serializers.ModelSerializer):
    # to accept either username or email
    user_name = serializers.CharField()
    password = serializers.CharField()
    user_type = serializers.CharField(required=False, read_only=True)
    token = serializers.CharField(required=False, read_only=True)

    def validate(self, data):
        # user,email,password validator
        user_name = data.get("user_name", None)
        password = data.get("password", None)
        if not user_name and not password:
            raise ValidationError("Details not entered.")
        user = None
        # if the email has been passed
        if '@' in user_name:
            user = User.objects.filter(
                Q(email=user_name) &
                Q(password=password)
            ).distinct()
            if not user.exists():
                raise ValidationError("User credentials are not correct.")
            user = User.objects.get(email=user_name)
        else:
            user = User.objects.filter(
                Q(username=user_name) &
                Q(password=password)
            ).distinct()
            if not user.exists():
                raise ValidationError("User credentials are not correct.")
            user = User.objects.get(username=user_name)
        if user.ifLogged:
            raise ValidationError("User already logged in.")
        user.ifLogged = True
        data['token'] = uuid4()
        temp = User.objects.get(username=user_name)
        data['user_type'] = temp.user_type
        data['user_id'] = temp.user_id
        user.token = data['token']
        user.user_type = data['user_type']
        user.user_id = data['user_id']
        user.save()
        return data

    class Meta:
        model = User
        fields = (
            'user_name',
            'password',
            'user_type',
            'token',
            'user_id'
        )

        read_only_fields = (
            'token',
            'user_type',
            'user_id'
        )


class UserLogoutSerializer(serializers.ModelSerializer):
    token = serializers.CharField()
    status = serializers.CharField(required=False, read_only=True)

    def validate(self, data):
        token = data.get("token", None)
        print(token)
        user = None
        try:
            user = User.objects.get(token=token)
            if not user.ifLogged:
                raise ValidationError("User is not logged in.")
        except Exception as e:
            raise ValidationError(str(e))
        user.ifLogged = False
        user.token = ""
        user.save()
        data['status'] = "User is logged out."
        return data

    class Meta:
        model = User
        fields = (
            'token',
            'status',
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = (
            'user_id',
        )


class UserSerializerWithType(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'user_type']
        read_only_fields = (
            'user_id',
        )


class ClassSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=Class.objects.all())]
    )

    class Meta:
        model = Class
        fields = ['class_id', 'class_name']
        read_only_fields = (
            'class_id',
        )


class SubjectSerializer(serializers.ModelSerializer):
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))
    is_archieved = serializers.ChoiceField(choices=BOOL_CHOICES)

    class Meta:
        model = Subject
        fields = ['subject_id', 'subject_name', 'user_id', 'class_id', 'is_archieved']
        read_only_fields = (
            'subject_id',
        )


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['test_id', 'test_name', 'subject_id', 'user_id']
        read_only_fields = (
            'test_id',
        )


class AssignedPupilSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedPupil
        fields = ['assign_id', 'class_id', 'user_id']
        read_only_fields = (
            'assign_id',
        )


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['grade_id', 'test_id', 'user_id', 'mark']
        read_only_fields = (
            'grade_id',
        )


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ('file',)
