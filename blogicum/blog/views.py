from django.http import Http404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView
from .models import Post, Category, User, Comment
from django.utils.timezone import now
from django.db.models import Count
from .forms import UserForm, PostForm, CommentForm

PAGINATE_COUNT = 10


class BaseMixin:
    model = Post


class UserProfileView(BaseMixin, ListView):
    template_name = "blog/profile.html"

    def get_queryset(self):
        self.username = get_object_or_404(User, slug=self.kwargs["username"])
        print(self.profile)


class BlogListView(BaseMixin, ListView):
    paginate_by = PAGINATE_COUNT
    template_name = "blog/index.html"

    def get_queryset(self, **kwargs):
        return (
            Post.get_posts(
                is_published=True, category__is_published=True,
                pub_date__lte=now(),
            )
            .select_related("author", "category", "location")
            .annotate(comment_count=Count("comments"))
            .filter(**kwargs)
            .order_by("-pub_date")
        )


class CategoryPostsView(BaseMixin, ListView):
    template_name = "blog/category.html"
    paginate_by = PAGINATE_COUNT

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        if not self.category.is_published:
            raise Http404
        return Post.objects.filter(
            category=self.category,
            is_published=True,
            category__is_published=True,
            pub_date__lte=now(),
        ).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class PostDetailView(BaseMixin, DetailView):
    template_name = "blog/detail.html"

    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        if self.request.user != post.author:
            if (
                post.pub_date > now()
                or not post.is_published
                or not post.category.is_published
            ):
                raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context["form"] = CommentForm(self.request.POST or None)
        context["comments"] = Comment.objects.select_related("author").filter(
            post=post)
        return context


def get_profile(request, username):
    profile = get_object_or_404(User, username=username)
    user_posts = Post.get_posts(author=profile)
    if request.user != profile:
        user_posts = Post.get_posts(
            is_published=True,
            category__is_published=True,
            pub_date__lte=now(),
            author=profile,
        )
    paginator = Paginator(user_posts, PAGINATE_COUNT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"profile": profile, "page_obj": page_obj}
    return render(request, "blog/profile.html", context)


@login_required
def edit_profile(request):
    profile = get_object_or_404(User, username=request.user)
    form = UserForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect("blog:profile", request.user)
    context = {"form": form}
    return render(request, "blog/user.html", context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("blog:profile", request.user)
    context = {"form": form}
    return render(request, "blog/create.html", context)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("blog:post_detail", post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id)
    context = {"form": form}
    return render(request, "blog/create.html", context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("blog:post_detail", post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == "POST":
        post.delete()
        return redirect("blog:index")
    context = {"form": form}
    return render(request, "blog/create.html", context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("blog:post_detail", post_id)
    context = {"form": comment}
    return render(request, "blog/comment.html", context)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария к публикации"""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect("blog:post_detail", post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id)
    context = {"comment": comment, "form": form}
    return render(request, "blog/comment.html", context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария к публикации"""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect("blog:post_detail", post_id)
    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id)
    context = {"comment": comment}
    return render(request, "blog/comment.html", context)
