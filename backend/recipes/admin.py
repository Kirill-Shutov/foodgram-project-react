from django.contrib import admin

from .models import Tag, Ingredient, Recipe 


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    # list_display = ('ingredients', 'author', 'tags', 'image', 'name', 'text', 'cooking_time')
    list_display = ('author', 'name',)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')