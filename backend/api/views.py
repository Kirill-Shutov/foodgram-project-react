from django.http.response import HttpResponse
from django.utils import timezone

import django_filters
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.permissions import CurrentUserOrAdmin, GetPost

from .filters import RecipeFilter
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .paginators import PageNumberPaginatorModified
from .serializers import (FavouriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):
    """Получение списка тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Получение списка ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    # def get_queryset(self):
    #     query = self.request.GET.get('name')
    #     return Ingredient.objects.filter(name__istartswith=query.lower())


class RecipeViewSet(viewsets.ModelViewSet):
    """Все действия с рецептами."""

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination
    permission_classes = (IsAuthorOrReadOnly,)

    def update(self, request, *args, **kwargs):
        if kwargs['partial'] is False:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже был добавлен.'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeFieldSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт уже был удален.'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, **kwargs):
        """Добавление рецепта в избранное или удаление из избранного."""
        try:
            recipe_id = int(self.kwargs.get('pk'))
        except ValueError:
            return Response(
                {
                    'message': (
                        'Рецепт с идентификатором '
                        f'{self.kwargs.get("pk")} не найден'
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'POST':
            return self.add_to(Favorite, request.user, pk=recipe_id)

        if request.method == 'DELETE':
            return self.delete_from(Favorite, request.user, recipe_id)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, **kwargs):
        """Добавление рецепта в список покупок или удаление из него."""
        try:
            recipe_id = int(self.kwargs.get('pk'))
        except ValueError:
            return Response(
                {
                    'message': (
                        'Рецепт с идентификатором '
                        f'{self.kwargs.get("pk")} не найден'
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk=recipe_id)

        if request.method == 'DELETE':
            return self.delete_from(ShoppingCart, request.user, recipe_id)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=('get', ),
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        """Скачивание ингредиентов из списка покупок."""
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__favorite_shops__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum(F('amount')))
            .order_by()
        )
        shop_list = []
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['amount']
            shop_list.append(
                f'\n{name} - {amount} {measurement_unit}')
        result = 'shop_list.txt'
        response = HttpResponse(
            shop_list,
            content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={result}'
        return response
