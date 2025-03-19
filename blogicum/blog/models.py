from django.db import models
from django.contrib.auth import get_user_model
from blogicum.models import BaseModel
from django.db.models import Count

User = get_user_model()

TEXT_LENGTH = 256


class Category(BaseModel):
    title = models.CharField("Заголовок", max_length=TEXT_LENGTH)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text=(
            "Идентификатор страницы для URL; "
            "разрешены символы латиницы, "
            "цифры, дефис и подчёркивание."
        ),
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"


class Location(BaseModel):
    name = models.CharField("Название места", max_length=TEXT_LENGTH)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"


class Post(BaseModel):
    title = models.CharField("Заголовок", max_length=TEXT_LENGTH)
    text = models.TextField("Текст")
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        help_text="Если установить дату и время в будущем — "
        "можно делать отложенные публикации.",
    )
    author = models.ForeignKey(
        User,
        related_name="posts",
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
    )
    location = models.ForeignKey(
        Location,
        null=True,
        related_name="posts",
        on_delete=models.SET_NULL,
        blank=True,
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        Category,
        null=True,
        related_name="posts",
        on_delete=models.SET_NULL,
        verbose_name="Категория",
    )
    image = models.ImageField("Фото", blank=True)

    @staticmethod
    def get_posts(**kwargs):
        return (
            Post.objects.select_related("category", "location", "author")
            .annotate(comment_count=Count("comments"))
            .filter(**kwargs)
            .order_by("-pub_date")
        )

    class Meta:
        ordering = ["-id"]
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"


class Comment(models.Model):
    text = models.TextField("Текст комментария")
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="Комментарий",
        related_name="comments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("created_at",)

    def __str__(self) -> str:
        return self.text
