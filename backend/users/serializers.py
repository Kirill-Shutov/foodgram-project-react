from recipes.models import Subscribe
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user,
                                        author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""
    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'email', 'username', 'password', 'first_name', 'last_name'
        )
