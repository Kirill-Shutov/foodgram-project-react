from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('email', 'first_name')
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'is_staff')
