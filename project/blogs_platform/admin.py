from blogs_platform import models
from django.contrib import admin


def hide_post(modeladmin, request, queryset):
    queryset.update(status='h')
hide_post.short_description = 'Make selected posts hidden'


def make_post_visible(modeladmin, request, queryset):
    queryset.update(status='v')
make_post_visible.short_description = 'Make selected posts visible'


class PostAdmin(admin.ModelAdmin):
    list_display = ('subject', 'text', 'status')
    actions = [hide_post, make_post_visible]


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author_nick', 'post', 'creation_date', 'reply_to')


admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Comment, CommentAdmin)
