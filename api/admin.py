from django.contrib import admin
# из файла models импортируем модель Post и Group
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("text", )
    list_filter = ("pub_date", 'text')
    empty_value_display = '-пусто-'


class PostGroup(admin.ModelAdmin):
    list_display = ('pk', 'title')


admin.site.register(Post, PostAdmin)
admin.site.register(Group, PostGroup)