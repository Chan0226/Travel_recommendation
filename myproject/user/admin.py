from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'user_pw', 'user_name', 'user_email',
                    'user_register_dttm', 'user_gender')

    list_display_links = ('id', 'user_id', 'user_pw', 'user_name',
                          'user_email', 'user_register_dttm', 'user_gender')
