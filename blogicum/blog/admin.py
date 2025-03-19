from django.contrib import admin
from .models import Category, Post, Location, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "slug", "is_published",
                    "created_at")
    list_editable = ("slug", "is_published")
    list_filter = ("title",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "text",
        "pub_date",
        "is_published",
        "author",
        "location",
        "category",
        "created_at",
    )
    list_editable = ("author", "location", "category", "is_published")
    list_filter = (
        "author",
        "location",
        "category",
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_published",
        "created_at",
    )
    list_editable = ("is_published",)
    list_filter = ("created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "post",
        "created_at",
    )
