from django.shortcuts import render
from rest_framework import generics

from .models import *
from .serializers import *
from .permissions import *
from rest_framework.response import Response
from rest_framework.views import APIView
from .pagination import *
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

class SupportAPIGet(generics.ListAPIView):
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


class FeedbackAPICanCreate(APIView):
    permission_classes = [IsCustomer, ]

    def get(self, request, pk):
        item = Movie.objects.get(pk=pk)
        items_ids = [order_item.item.id for order_item in Ticket.objects.filter(session__in=Session.objects.filter(
            user=request.user, delivered_at__isnull=False))]
        if item.id in items_ids:
            return Response({'message': 'success'})
        raise ValidationError("You can't leave a feedback because you haven't purchased this item yet")


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


class FeedbackAPICreate(APIView):
    permission_classes = [IsCustomer, ]

    def post(self, request):
        feedback_data = request.data
        Feedback.objects.create(item_id=feedback_data['item_id'], description=feedback_data[
            'description'], user=request.user, rating=feedback_data['rating'])
        movie = Movie.objects.get(id=feedback_data['item_id'])
        movie.rating = Feedback.objects.filter(movie=movie).aggregate(Movie('rating'))['rating__avg']
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

