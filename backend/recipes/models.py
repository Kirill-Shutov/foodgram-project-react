from django.db import models
from django.core.validators import MinValueValidator
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

    def __str__(self):
        return f'{self.name} ({self.measurement_unit}) - {self.amount}'


class Recipe(models.Model):
    """Сам рецепт со всеми составляющими."""
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='ingredients_recipes',
        through='recipes.AmountIngredient'
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='author_rec'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Тэги рецепта',
        related_name='tags_recipes'
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
        verbose_name='Время приготовления (в минутах)'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
    
    def __str__(self):
        return f'{self.name[:20]}, {self.author.username}'


class Subscribe(models.Model):
    """Подписка на авторов рецепта."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        # ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='уникальная подписка'
            )
        ]
    
    def __str__(self):
        return f'Пользователь {self.user} подписался на {self.author}'
    

class FavoriteRecipe(models.Model):
    """Добавление рецептов в избранное."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='user_favorite_unique'
            )
        ]
    
    def __str__(self):
        return f'Пользователь {self.user} добавил {self.name.Recipe} в избранные.'


class AmountIngredient(models.Model):
    """Количество ингридиентов в рецепте.
    Модель связывает Recipe и Ingredient количеством ингридиентов.
    """
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='В каких рецептах',
        related_name='ingredient'
    )
    ingredients = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Связанные ингредиенты',
        related_name='recipes'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        # related_name='amounts',
        default=0,
        validators=[MinValueValidator(
            1, message='Минимальное количество 1!'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'ingredients'],
            name='Избранные рецепты'
            )
        ]
    
    def __str__(self):
        return f'{self.ingredients} {self.amount}'


class ShoppingCart(models.Model):
    """Лист покупок."""
    user = models.ForeignKey(
        CustomUser, related_name='purchases',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, related_name='customers',
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
    
    def __str__(self):
        return f'{self.user} - {self.recipe}'