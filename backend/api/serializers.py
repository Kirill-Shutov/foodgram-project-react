# from djoser.serializers import UserCreateSerializer, UserSerializer
# from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            AmountIngredient, ShoppingCart, Tag,
                            Subscribe)
from users.models import CustomUser
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра модели Tag."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class AmountIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели, связывающей ингредиенты и рецепт."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ['id', 'name', 'amount', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра модели Recipe."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_ingredients(self, obj):
        ingredients = AmountIngredient.objects.filter(recipe=obj)
        return AmountIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()
    

class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ['id', 'amount']


# class CreateRecipeSerializer(serializers.ModelSerializer):
#     """Сериализатор создания/обновления рецепта."""

#     author = CustomUserCreateSerializer(read_only=True)
#     ingredients = AddIngredientSerializer(many=True)
#     tags = serializers.PrimaryKeyRelatedField(
#         queryset=Tag.objects.all(), many=True
#     )
#     image = Base64ImageField()

#     class Meta:
#         model = Recipe
#         fields = [
#             'id',
#             'author',
#             'ingredients',
#             'tags',
#             'image',
#             'name',
#             'text',
#             'cooking_time'
#         ]

#     def validate(self, data):
#         ingredients = self.initial_data.get('ingredients')
#         list = []
#         for i in ingredients:
#             amount = i['amount']
#             if int(amount) < 1:
#                 raise serializers.ValidationError({
#                    'amount': 'Количество ингредиента должно быть больше 0!'
#                 })
#             if i['id'] in list:
#                 raise serializers.ValidationError({
#                    'ingredient': 'Ингредиенты должны быть уникальными!'
#                 })
#             list.append(i['id'])
#         return data

#     def create_ingredients(self, ingredients, recipe):
#         for i in ingredients:
#             ingredient = Ingredient.objects.get(id=i['id'])
#             Ingredient.objects.create(
#                 ingredient=ingredient, recipe=recipe, amount=i['amount']
#             )

#     def create_tags(self, tags, recipe):
#         for tag in tags:
#             Tag.objects.create(recipe=recipe, tag=tag)

#     def create(self, validated_data):
#         """
#         Создание рецепта.
#         Доступно только авторизированному пользователю.
#         """

#         ingredients = validated_data.pop('ingredients')
#         tags = validated_data.pop('tags')
#         author = self.context.get('request').user
#         recipe = Recipe.objects.create(author=author, **validated_data)
#         self.create_ingredients(ingredients, recipe)
#         self.create_tags(tags, recipe)
#         return recipe

#     def update(self, instance, validated_data):
#         """
#         Изменение рецепта.
#         Доступно только автору.
#         """

#         RecipeTag.objects.filter(recipe=instance).delete()
#         RecipeIngredient.objects.filter(recipe=instance).delete()
#         ingredients = validated_data.pop('ingredients')
#         tags = validated_data.pop('tags')
#         self.create_ingredients(ingredients, instance)
#         self.create_tags(tags, instance)
#         instance.name = validated_data.pop('name')
#         instance.text = validated_data.pop('text')
#         if validated_data.get('image'):
#             instance.image = validated_data.pop('image')
#         instance.cooking_time = validated_data.pop('cooking_time')
#         instance.save()
#         return instance

#     def to_representation(self, instance):
#         return RecipeSerializer(instance, context={
#             'request': self.context.get('request')
#         }).data


# class ShowFavoriteSerializer(serializers.ModelSerializer):
#     """ Сериализатор для отображения избранного. """

#     class Meta:
#         model = Recipe
#         fields = ['id', 'name', 'image', 'cooking_time']


# class ShoppingCartSerializer(serializers.ModelSerializer):
#     """ Сериализатор для списка покупок. """

#     class Meta:
#         model = ShoppingCart
#         fields = ['user', 'recipe']

#     def to_representation(self, instance):
#         return ShowFavoriteSerializer(instance.recipe, context={
#             'request': self.context.get('request')
#         }).data


# class FavoriteSerializer(serializers.ModelSerializer):
#     """ Сериализатор модели Избранное. """

#     class Meta:
#         model = Favorite
#         fields = ['user', 'recipe']

#     def to_representation(self, instance):
#         return ShowFavoriteSerializer(instance.recipe, context={
#             'request': self.context.get('request')
#         }).data


# class ShowSubscriptionsSerializer(serializers.ModelSerializer):
#     """ Сериализатор для отображения подписок пользователя. """

#     is_subscribed = serializers.SerializerMethodField()
#     recipes = serializers.SerializerMethodField()
#     recipes_count = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = [
#             'id',
#             'email',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed',
#             'recipes',
#             'recipes_count'
#         ]

#     def get_is_subscribed(self, obj):
#         request = self.context.get('request')
#         if request is None or request.user.is_anonymous:
#             return False
#         return Subscription.objects.filter(
#             user=request.user, author=obj).exists()

#     def get_recipes(self, obj):
#         request = self.context.get('request')
#         if not request or request.user.is_anonymous:
#             return False
#         recipes = Recipe.objects.filter(author=obj)
#         limit = request.query_params.get('recipes_limit')
#         if limit:
#             recipes = recipes[:int(limit)]
#         return ShowFavoriteSerializer(
#             recipes, many=True, context={'request': request}).data

#     def get_recipes_count(self, obj):
#         return Recipe.objects.filter(author=obj).count()


# class SubscriptionSerializer(serializers.ModelSerializer):
#     """ Сериализатор подписок. """

#     class Meta:
#         model = Subscription
#         fields = ['user', 'author']
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Subscription.objects.all(),
#                 fields=['user', 'author'],
#             )
#         ]

#     def to_representation(self, instance):
#         return ShowSubscriptionsSerializer(instance.author, context={
#             'request': self.context.get('request')
#         }).data