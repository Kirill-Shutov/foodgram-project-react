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
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            1, message='Минимальное количество 1!'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - ({self.measurement_unit})'


class Recipe(models.Model):
    """Сам рецепт со всеми составляющими."""
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='ingredients_recipes',
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='author_recipes'
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
