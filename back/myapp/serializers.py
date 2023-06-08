import re

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
    role_id = serializers.IntegerField(required=False)
    role = serializers.CharField(read_only=True)
    phone = serializers.CharField()

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        photo_file = validated_data.pop('photo', None)
        validated_data['phone'] = re.sub(r'[() -]', '', validated_data['phone'])
        instance = User(**validated_data)
        instance.role = Role.objects.get(name_en='customer')
        if photo_file:
            photo_type = str(photo_file).split('.')[-1]
            photo = base64.b64encode(photo_file.read())
            photo_text = f'data:image/{photo_type};base64,' + photo.decode()
            instance.photo = photo_text
        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance


class AdminUserUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64, required=False)
    photo = serializers.ImageField(required=False)
    role_id = serializers.IntegerField(required=False)
    photo_base64 = serializers.CharField(source='photo', read_only=True)

    def update(self, instance, validated_data):
        photo_file = validated_data.pop('photo', None)
        instance.name = validated_data.get("name", instance.name)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.role_id = validated_data.get('role_id', instance.role_id)
        if photo_file:
            photo_type = str(photo_file).split('.')[-1]
            photo = base64.b64encode(photo_file.read())
            photo_text = f'data:image/{photo_type};base64,' + photo.decode()
            instance.photo = photo_text
        instance.save()
        return instance


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name', 'name_en')


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
    movie_name = serializers.CharField(source='movie.name', read_only=True)
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


class SessionSerializer(serializers.ModelSerializer):
    movie_id = serializers.IntegerField()
    movie_name = serializers.CharField(source='movie.name', read_only=True)
    movie_duration = serializers.IntegerField(source='movie.duration', read_only=True)
    movie_photo_url = serializers.CharField(source='movie.photo.url', read_only=True)
    movie_genres = serializers.StringRelatedField(source='movie.genres', many=True, read_only=True)
    movie_description = serializers.CharField(source='movie.description', read_only=True)
    hall_id = serializers.IntegerField()
    hall_name = serializers.CharField(source='hall.name', read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'movie_id', 'movie_name', 'movie_duration', 'movie_photo_url', 'movie_genres',
                  'movie_description', 'hall_id',
                  'hall_name', 'time', 'price']


class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    session_time = serializers.DateTimeField(source='session.time', read_only=True)
    session_price = serializers.IntegerField(source='session.price', read_only=True)
    movie_id = serializers.IntegerField(source='session.movie.id', read_only=True)
    movie_name = serializers.CharField(source='session.movie.name', read_only=True)
    movie_duration = serializers.IntegerField(source='session.movie.duration', read_only=True)

    hall_name = serializers.CharField(source='session.hall.name', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'created_at', 'session_id', 'session_time', 'session_price', 'movie_id', 'movie_name',
                  'movie_duration',
                  'hall_name', 'row', 'seat', 'status']


class NewsSerializer(serializers.ModelSerializer):
    photo_url = serializers.CharField(source='photo.url', read_only=True)

    class Meta:
        model = News
        fields = ('id', 'title', 'description', 'photo', 'photo_url', 'created_at')
        extra_kwargs = {
            'photo': {'write_only': True}
        }

    def create(self, validated_data):
        new = News(**validated_data)
        new.save()
        return new

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {k: v for k, v in data.items() if v is not None}

class MovieSerializer(serializers.ModelSerializer):
    def get_feedback_count(self, obj):
        return obj.get_feedback_count()

    def get_feedbacks(self, obj):
        feedbacks = obj.get_feedbacks().filter(publish=True)

        serializer = FeedbackSerializer(feedbacks, many=True)
        return serializer.data

    photo_url = serializers.CharField(source='photo.url', read_only=True)
    # genres = serializers.StringRelatedField(many=True)
    feedback_count = serializers.SerializerMethodField()
    # feedbacks = FeedbackSerializer(many=True, read_only=True, source='feedback_set', filter_required=True)
    feedbacks = serializers.SerializerMethodField()
    class Meta:
        model = Movie
        fields = ['id', 'name', 'description', 'duration', 'age_limit', 'photo', 'photo_url', 'rating',
                  'feedback_count', 'feedbacks']
        extra_kwargs = {
            'photo': {'write_only': True},
            'rating': {'read_only': True},
            'feedback_count': {'read_only': True},
        }

    def create(self, validated_data):
        rating = validated_data.pop('rating', None)
        movie = Movie(**validated_data)
        movie.save()
        return movie


# class GenreSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Genre
#         fields = ['id', 'name']
