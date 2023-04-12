from django_filters import BooleanFilter, CharFilter, FilterSet, ModelMultipleChoiceFilter

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    # tags = CharFilter(field_name='tags__slug', method='filter_tags')
    tags = ModelMultipleChoiceFilter(field_name='tags__slug', queryset=Tag.objects.all(), to_field_name ='slug')
    is_favorited = BooleanFilter(
        method='get_favorite',
        field_name='is_favorited'
    )
    is_in_shopping_cart = CharFilter(
        method='get_is_in_shopping_cart',
        field_name='is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    # def filter_tags(self, queryset, slug, tags):
    #     tags = self.request.query_params.getlist('tags')
    #     return queryset.filter(
    #         tags__slug__in=tags
    #     ).distinct()

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
