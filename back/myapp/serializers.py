from rest_framework import serializers
from .models import *

from rest_framework import serializers
from .models import *
import base64


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=255, write_only=True)
    email = serializers.EmailField()
    photo = serializers.ImageField(required=False)
    photo_base64 = serializers.CharField(source='photo', read_only=True)
    role_id = serializers.IntegerField()
    role = serializers.CharField(read_only=True)
    phone = serializers.CharField()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        photo_file = validated_data.pop('photo', None)

        instance = User(**validated_data)
        instance.role = Role.objects.get(name='Пользователь')
        if photo_file:
            photo_type = str(photo_file).split('.')[-1]
            photo = base64.b64encode(photo_file.read())
            photo_text = f'data:image/{photo_type};base64,' + photo.decode()
            instance.photo = photo_text
        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance


class SupportSerializer(serializers.ModelSerializer):

    def get_file_url(self, obj):
        return obj.get_file_url()
    user_id = serializers.IntegerField(read_only=True)

    file_url = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Support
        fields = ('id', 'description', 'created_at', 'file', 'file_url', 'user_id', 'user_name',
                  'user_phone', 'solved')
        extra_kwargs = {
            'file': {'write_only': True}
        }

    def create(self, validated_data):
        description = validated_data.get('description')
        file = validated_data.get('file')
        item = Support.objects.create(description=description, file=file, user=self.context['request'].user)

        item.save()
        return item

class FeedbackSerializer(serializers.ModelSerializer):
    movie_id = serializers.IntegerField()
    movie_name = serializers.CharField(source='item.name', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Feedback
        fields = ('id', 'movie_id', 'movie_name', 'description', 'created_at', 'user_name', 'rating', 'publish')
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def update(self, instance, validated_data):
        instance.publish = validated_data.get('publish')
        instance.save()
        return instance
