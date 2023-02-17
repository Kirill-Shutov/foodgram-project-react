from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """ Кастомная модель пользователя. """
    first_name = models.TextField(
        'Имя',
        blank=False,
        max_length=150,
        help_text='Не больше 150 символов'
    )
    last_name = models.TextField(
        'Фамилия',
        blank=False,
        max_length=150,
        help_text='Не больше 150 символов'
    )
    email = models.EmailField(
        'Адрес почты',
        blank=False,
        unique=True,
        help_text='Введите почту'
    )
    username = models.CharField(
        'Логин',
        blank=False,
        max_length=150,
        help_text='Придумайте логин'
    )
    password = models.CharField(
        'Пароль',
        blank=False,
        max_length=150,
        help_text='Придумайте пароль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
