from django.contrib import admin

from . import models


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class AmountIngredientInLine(admin.TabularInline):
    model = models.AmountIngredient
    min_num = 1


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name',)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    inlines = (AmountIngredientInLine,)


@admin.register(models.Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')


@admin.register(models.FavoriteRecipe)
class FavoriteRecipe(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(models.ShoppingCart)
class ShoppingCart(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
