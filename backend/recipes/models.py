from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    """Поле Tag в рецептах."""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=150,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет тега',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Фрагмент тега',
        max_length=64,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug',)

    def __str__(self):
        return f'{self.name[:20]}'


class Ingredient(models.Model):
    """Поле ингредиентов в рецепте
    с указанием количества и единицы измерения.
    """
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=64,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=32
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Сам рецепт со всеми составляющими."""
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='AmountIngredient'
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Тэги рецепта',
        related_name='recipes'
    )
    image = models.ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipes/'
    )
    name = models.CharField(
        verbose_name='Название блюда',
        max_length=200
    )
    text = models.TextField(
        verbose_name='Описание блюда'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=(
            MinValueValidator(
                1, message='Уже все готово!'
            ),
            MaxValueValidator(
                300, message='Кажется все сгорит!'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='уникальный для автора'
            )
        ]
        ordering = ('name',)

    def __str__(self):
        return f'{self.name[:20]}, {self.author.username}'


class AmountIngredient(models.Model):
    """Количество ингридиентов в рецепте.
    Модель связывает Recipe и Ingredient количеством ингридиентов.
    """
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='В каких рецептах',
        related_name='amounts'
    )
    ingredients = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Связанные ингредиенты',
        related_name='amounts'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0, null=True, blank=True,
        validators=(
            MinValueValidator(
                1, message='Минимальное количество 1!'
            ),
            MaxValueValidator(
                30, message='Слишком много, проверь!'
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredients'],
            name='Избранные рецепты'
            )
        ]
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.ingredients} {self.amount}'


class Subscribe(models.Model):
    """Подписка на авторов рецепта."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscription_on'
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='subscriber'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='уникальная подписка'
            )
        ]
        ordering = ('author',)

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'


class FavoriteRecipe(models.Model):
    """Добавление рецептов в избранное."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='уникальный избранный автор'
            )
        ]
        ordering = ('recipe',)

    def __str__(self):
        return f'Пользователь {self.user} добавил {self.recipe} в избранные.'


class ShoppingCart(models.Model):
    """Лист покупок."""
    user = models.ForeignKey(
        CustomUser, related_name='shopping_cart',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, related_name='shopping_cart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок для рецепта'
        verbose_name_plural = 'Списки покупок для рецепта'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='recipe_unique'
            )
        ]
        ordering = ('recipe',)
        

    def __str__(self):
        return f'{self.user} - {self.recipe}'
