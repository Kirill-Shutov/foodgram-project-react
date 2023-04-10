from drf_extra_fields.fields import Base64ImageField
from recipes.models import (AmountIngredient, FavoriteRecipe, Ingredient,
                            Recipe, ShoppingCart, Tag, TagRecipe)
from rest_framework import serializers
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

    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ['id', 'name', 'amount', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра модели Recipe."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = AmountIngredientSerializer(many=True, source='amounts')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')
    image = Base64ImageField()

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

    def get_amount(self, obj):
        return None

    def get_is_favorited(self, obj):
        """Находится ли рецепт в избранном."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Находится ли рецепт в списке покупок."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe_id=obj
        ).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения избранных рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteCreateSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в избранное."""

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        """Получение избранного."""
        return FavoriteSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ['id', 'amount']


class SubscribeSerializer(UserSerializer):
    """Сериализатор для отображения подписок пользователя."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'recipes', 'recipes_count', 'is_subscribed'
        )
        model = CustomUser
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return FavoriteSerializer(
            recipes, many=True, context={'request': request}).data

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей."""
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.subscriber.filter(user=user).exists()

    def get_recipes_count(self, obj):
        """Показывает количество рецептов автора."""
        return Recipe.objects.filter(author=obj).count()


class ShoppingCartCreateSerializer(serializers.ModelSerializer):
    """Сериализатор добавления в список покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания/обновления рецепта."""

    author = UserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]

    def validate(self, data):
        """Проверка количества ингредиентов и уникальности."""
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        for ingredient in ingredients:
            amount = ingredient['amount']
            if int(amount) < 1:
                raise serializers.ValidationError({
                   'amount': 'Количество ингредиента должно быть больше 0!'
                })
            if int(amount) > 32000:
                raise serializers.ValidationError({
                   'amount': 'Количество не должно быть больше 32000!'
                })
            identifier = ingredient.get('id')
            if identifier in ingredients_set:
                raise serializers.ValidationError({
                   'ingredient': 'Ингредиенты должны быть уникальными!'
                })
            ingredients_set.add(identifier)
        return data

    def create_ingredients(self, ingredients, recipe):
        """Создание ингредиентов."""
        AmountIngredient.objects.bulk_create(
            [AmountIngredient(
                ingredients=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create_tags(self, tags, recipe):
        """Создание тегов."""
        TagRecipe.objects.bulk_create(
            [TagRecipe(
                tags=Tag.objects.get(name=tag_data),
                recipe=recipe,
            ) for tag_data in tags]
        )

    def create(self, validated_data):
        """Создание рецепта.
        Доступно только авторизированному пользователю.
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        ingredients = self.create_ingredients(ingredients, recipe)
        tags = self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта. Доступно только автору"""
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        instance.tags.clear()
        tags = validated_data.get('tags')
        self.create_tags(tags, instance)

        AmountIngredient.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.get('ingredients')
        self.create_ingredients(ingredients, instance)

        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data
