from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import SubscribeSerializer
from recipes.models import Subscribe

from .permissions import GetPost
from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [GetPost]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = (
            User.objects
            .filter(subscriber__user=request.user)
            .order_by('id')
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscribeSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['get', 'delete', 'post'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        if not pk and 'author_id' not in request.data:
            return Response(
                data={'errors': 'Не указан параметр author_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if pk:
            author = get_object_or_404(User, pk=pk)
        else:
            author_id = request.data.get('author_id')
            author = get_object_or_404(User, pk=author_id)

        if author == request.user:
            return Response(
                data={'errors': 'Вы не можете подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscribed = author.subscriber.filter(user=request.user).exists()

        if request.method == 'GET':
            if subscribed:
                return Response(
                    data={'errors': 'Вы уже подписались на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = UserSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'POST':
            if subscribed:
                return Response(
                    data={'errors': 'Вы уже подписались на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.create(user=request.user, author=author)
            serializer = UserSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not subscribed:
                return Response(
                    data={'errors': 'Вы не были подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscribe.objects.filter(user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
