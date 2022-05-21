from django.contrib import admin
from .models import *
# from .models import User

# Register your models here.


class HotelAdmin(admin.ModelAdmin):
    list_display = ('index', 'place', 'name', 'rating', 'distance', 'cost',
                    'address', 'explain', 'kind', 'clean', 'conv', 'url',
                    'img', 'classfication')


class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('index', 'place', 'name', 'rating', 'review',
                    'classfication', 'address', 'explain', 'url', 'img')


class TourAdmin(admin.ModelAdmin):
    list_display = ('index', 'place', 'rating', 'review', 'classfications',
                    'address', 'explain', 'mood', 'topic', 'reason', 'cluster')


class MergeAdmin(admin.ModelAdmin):
    list_display = ('index', '장소', '아이디', '평점', '평균평점', '리뷰개수', '구분', '주소',
                    '설명', 'like')


class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'user', 'hotel', 'restaurant', 'tour')


admin.site.register(Hotel, HotelAdmin)

admin.site.register(Restaurant, RestaurantAdmin)

admin.site.register(Tour, TourAdmin)

admin.site.register(Merge, MergeAdmin)

admin.site.register(Cart, CartAdmin)