from django.db.models import F, Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (AmountIngredient, FavoriteRecipe, Ingredient,
                            Recipe, ShoppingCart, Tag)
from users.permissions import CurrentUserOrAdmin, GetPost

from .filters import RecipeFilter
from .pagination import SixItemPagination
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение списка ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Все действия с рецептами."""
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = SixItemPagination
    permission_classes = [GetPost, CurrentUserOrAdmin]

    def update(self, request, *args, **kwargs):
        if kwargs['partial'] is False:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже добавлен.'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(recipe)
        serializer.create(user=user, recipe=recipe)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт уже удален.'},
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
            return self.add_to(FavoriteRecipe, request.user, pk=recipe_id)

        if request.method == 'DELETE':
            return self.delete_from(FavoriteRecipe, request.user, recipe_id)
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
            AmountIngredient.objects
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
