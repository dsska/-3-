from django.contrib import admin

from blog.models import Category, Location, Post, Comment


def get_model_fields(model):
    return model._meta.get_fields()


class BlogAdmin(admin.ModelAdmin):
    list_editable = ('is_published',)


@admin.register(Post)
class PostAdmin(BlogAdmin):

    list_display = [
        field.name
        for field in get_model_fields(Post)
        if field.name not in ('id', 'text')
    ]
    list_display_links = ("title",)
    search_fields = (
        'title',
        'text',
    )
    list_filter = (
        'is_published',
        'category',
        'location',
        'author',
    )


@admin.register(Category)
class CategoryAdmin(BlogAdmin):

    list_display = (
        'title',
        'is_published',
        'created_at',
        'slug',
    )


@admin.register(Location)
class LocationAdmin(BlogAdmin):

    list_display = (
        'name',
        'is_published',
        'created_at',
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'post',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'text',
        'author__username',
    )
