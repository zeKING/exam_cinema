import re

from datetime import datetime, timezone

import requests
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, Avg
from django.shortcuts import render
from rest_framework import generics

from .models import *
from .serializers import *
from .permissions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from .pagination import *
from django.forms.models import model_to_dict
import pyclick
from rest_framework.permissions import IsAuthenticated
# Create your views here.


class RegisterView(APIView):

    authentication_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated, ]
#
#     def post(self, request):
#         response = Response()
#         # response.delete_cookie('jwt')
#         refresh_token = request.data['refresh']
#         token = RefreshToken(refresh_token)
#         token.blacklist()
#
#         response.data = {
#             'message': 'success'
#         }
#         return response


class UserAPIGet(APIView):
    # queryset = User.objects.all()
    # serializer_class = UserSerializer
    # permission_classes = [IsAuthenticated, ]

    def get(self, request):
        # user = User.objects.get(pk=request.user.id)
        return Response({
            'id': request.user.id,
            'phone': request.user.phone,
            'name': request.user.name,
            'email': request.user.email,
            'photo': request.user.photo,
            'role': request.user.role.name,
            'role_en': request.user.role.name_en
        })


class UserAPIGetAll(generics.ListAPIView):

    def get_queryset(self):
        search = ''
        if self.request.query_params.get('search'):
            search += self.request.query_params.get('search')
        if int(self.request.query_params.get('role_id')) == -1:
            return User.objects.filter(Q(
                name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search))
        else:
            return User.objects.filter(Q(role_id=int(self.request.query_params.get('role_id'))) & (Q(
                name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search)))

    serializer_class = UserSerializer
    permission_classes = [IsAdmin, ]
    pagination_class = UserPagination


class AdminUserAPIDelete(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdmin, ]


class AdminUserAPIUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserUpdateSerializer
    permission_classes = [IsAdmin, ]


class RoleAPIGetAll(generics.ListAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin, ]


class AdminSupportAPIGet(generics.ListAPIView):
    def get_queryset(self):
        search = ''
        if self.request.query_params.get('search'):
            search += self.request.query_params.get('search')
        status = self.request.query_params.get('status')
        if status == 'all':
            return Support.objects.filter(description__icontains=search)
        elif status == 'solved':
            return Support.objects.filter(solved=True, description__icontains=search)
        elif status == 'unsolved':
            return Support.objects.filter(solved=False, description__icontains=search)
        else:
            return None
    pagination_class = SupportPagination
    serializer_class = SupportSerializer
    permission_classes = [IsAdmin, ]


class SupportAPICreate(generics.CreateAPIView):
    queryset = Support.objects.all()
    serializer_class = SupportSerializer
    permission_classes = [IsCustomer, ]


class SupportAPIUpdate(APIView):
    permission_classes = [IsAdmin, ]

    def patch(self, request, pk):
        support = Support.objects.filter(id=pk).first()
        support.solved = request.data.get('solved')
        support.save()
        return Response({'message': 'success'})


class FeedbackAPICanCreate(APIView):
    permission_classes = [IsCustomer, ]

    def get(self, request, pk):
        movie = Movie.objects.get(pk=pk)
        tickets = Ticket.objects.filter(session__in=Session.objects.filter(
            movie=movie), owner=request.user, status=2)
        if tickets:
            return Response({'message': 'success'})
        raise ValidationError("You can't leave a feedback because you haven't purchased this item yet")


class FeedbackAPICreate(APIView):
    permission_classes = [IsCustomer, ]

    def post(self, request):
        feedback_data = request.data
        Feedback.objects.create(movie_id=feedback_data['item_id'], description=feedback_data[
            'description'], user=request.user, rating=feedback_data['rating'])
        movie = Movie.objects.get(id=feedback_data['item_id'])
        movie.rating = Feedback.objects.filter(movie=movie).aggregate(Avg('rating'))['rating__avg']
        movie.save()
        return Response({"message": "feedback was successfully created"})


class AdminFeedbackAPIGetAll(generics.ListAPIView):
    def get_queryset(self):
        search = ''
        if self.request.query_params.get('search'):
            search += self.request.query_params.get('search')
        status = self.request.query_params.get('status')
        if status == 'published':
            return Feedback.objects.filter(publish=True, description__icontains=search)
        elif status == 'unpublished':
            return Feedback.objects.filter(publish=False, description__icontains=search)
        else:
            return Feedback.objects.all()

    serializer_class = FeedbackSerializer
    permission_classes = [IsAdmin, ]
    pagination_class = FeedbackPagination


class AdminFeedbackAPIUpdate(generics.UpdateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAdmin, ]


class HallAPIGetALL(generics.ListAPIView):
    queryset = Hall.objects.all()
    serializer_class = HallSerializer
    permission_classes = [IsCustomer, ]


# class GenreAPIGetAll(generics.ListAPIView):
#     queryset = Genre.objects.all()
#     serializer_class = GenreSerializer


class MovieAPIGetAll(generics.ListAPIView):
    def get_queryset(self):
        search = ''
        if self.request.query_params.get('search'):
            search += self.request.query_params.get('search')
        return Movie.objects.filter(name__icontains=search)
    serializer_class = MovieSerializer
    pagination_class = MoviePagination


class MovieAPICreate(generics.CreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAdmin, ]


class MovieAPIUpdate(generics.UpdateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAdmin, ]


class MovieAPIDelete(generics.DestroyAPIView):
    queryset = Movie.objects.all()
    permission_classes = [IsAdmin, ]


class MovieAPIGet(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related('feedback_set')  # Загрузка связанных обратных связей
        return queryset

class SessionAPICreate(APIView):
    permission_classes = [IsSalesman, ]

    def post(self, request):
        data = request.data
        session_serializer = SessionSerializer(data=request.data)
        session_serializer.is_valid(raise_exception=True)
        session = Session.objects.create(movie_id=data['movie_id'], hall_id=data['hall_id'], time=data['time'],
                                         price=data['price'])

        hall = Hall.objects.get(id=data['hall_id'])

        for i in range(hall.rows):
            for j in range(hall.seats):
                Ticket.objects.create(session=session, row=i+1, seat=j+1)
        return Response({'session': SessionSerializer(session).data})


class SessionAPIGet(generics.RetrieveAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer


class SessionAPIGetAll(generics.ListAPIView):
    def get_queryset(self):
        if self.request.query_params.get('movie'):
            return Session.objects.filter(movie_id=self.request.query_params.get('movie'))
        else:
            return Session.objects.all()
    serializer_class = SessionSerializer
    pagination_class = SessionPagination


class SessionAPIUpdate(generics.UpdateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsSalesman, ]


class SessionAPIDelete(generics.DestroyAPIView):
    queryset = Session.objects.all()
    permission_classes = [IsSalesman, ]




class TicketAPICreate(APIView):
    # permission_classes = [IsCustomer, ]

    def post(self, request):
        d = request.data
        phone = re.sub(r'[() -]', '', d['phone'])
        phone = validate_uzb_phone(phone)
        ticket = Ticket.objects.filter(session_id=d['session_id'], row=d['row'], seat=d['seat']).first()

        # if ticket.status == 1:
        #     if (datetime.now(timezone.utc) - ticket.updated_at).seconds < 300:
        #         raise ValidationError("Это место забронировано")
        if ticket.status == 2:
            return Response({'message': 'Место уже занято или его не существует'})
        if type(request.user) == User:
            ticket.owner = request.user
        else:
            ticket.tg_owner_id = d['user_id']
        ticket.status = 2
        ticket.phone = phone
        # transaction = ClickTransaction.objects.create(amount=Session.objects.get(id=d['session_id']).price)
        # ticket.transaction = transaction
        # phone_num = re.sub('[ +\-()]', '', d['phone'])
        # requests.post('http://127.0.0.1:8000/pyclick/process/click/service/create_invoice',
        #               {'phone_number': phone_num, 'transaction_id': transaction.id})
        ticket.save()
        return Response({'message': 'Место успешно забронировано'})


class TicketAPIGetAll(APIView):
    def get(self, request):
        session = Session.objects.get(id=request.query_params['session'])
        tickets = Ticket.objects.filter(session=session)
        hall = session.hall
        rows = []
        for i in range(hall.rows):
            temp = []
            for j in range(hall.seats):
                ticket = tickets.get(row=i+1, seat=j+1)
                print(ticket)
                # serializer = TicketSerializer(data=model_to_dict(ticket))
                # serializer.is_valid(raise_exception=True)
                temp.append(model_to_dict(ticket))
            rows.append(temp)
        return Response({'rows': rows})


class TicketAPIUpdate(APIView):
    permission_classes = [IsSalesman, ]

    def patch(self, request, pk):
        status = int(request.data['status'])
        if not (0 <= status <= 3):
            raise ValidationError('wrong status')
        ticket = Ticket.objects.get(id=pk)
        if status == 2 and ticket.status != 1:
            raise ValidationError('Нельзя так')
        if status == 1 and ticket.status != 2:
            raise ValidationError('Нельзя так')
        if status == 3 and ticket.status != 0:
            raise ValidationError('нельзя так')
        if status == 0 and ticket.status != 3:
            raise ValidationError('нельзя так')
        ticket.status = status
        ticket.editor = request.user
        ticket.save()
        return Response({'message': 'success'})


class TicketAPIDelete(APIView):

    def delete(self, request, pk):
        ticket = Ticket.objects.get(id=pk)
        if type(request.user) == User:
            if request.user != ticket.owner:
                return Response({'message': 'Тебе сюда низя'})
        else:
            if int(request.data['user_id']) != ticket.tg_owner_id:
                return Response({'message': 'Тебе сюда низя'})
        # if ticket.transaction.status == 'confirmed':
        #     requests.post('http://127.0.0.1:8000/pyclick/process/click/service/cancel_payment',
        #                   {'transaction_id': ticket.transaction.id})
        ticket.status = 0
        ticket.editor = None
        ticket.owner = None
        ticket.tg_owner_id = None
        ticket.phone = None
        ticket.save()
        return Response({'message': 'success'})
        # raise ValidationError('hahaha')


class TicketAPIGetMy(generics.ListAPIView):
    def get_queryset(self):
        print(type(self.request.user))
        if type(self.request.user) == User:
            return Ticket.objects.filter(owner=self.request.user, status=2)
        else:
            return Ticket.objects.filter(tg_owner_id=self.request.data['user_id'], status=2)
    serializer_class = TicketSerializer
    pagination_class = TicketPagination


class NewsAPIGetAll(generics.ListAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    authentication_classes = []
    pagination_class = NewsPagination


class NewsAPICreate(generics.CreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAdmin, ]


class NewsAPIUpdate(generics.UpdateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAdmin, ]


class NewsAPIDelete(generics.DestroyAPIView):
    queryset = News.objects.all()
    permission_classes = [IsAdmin, ]
