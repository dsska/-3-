from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from blog.utils import query_category, filter_and_annotate_posts, paginate_queryset
from .forms import PostForm, CommentForm, UserUpdateForm
from .models import Post, Comment


User = get_user_model()




def index(request):
    posts = filter_and_annotate_posts(order_by='-pub_date')
    page_obj = paginate_queryset(request, posts)
    context = {'post_list': page_obj}
    return render(request, 'blog/index.html', context)



def post_detail(request, post_id):
    # First, try to get the post from the full table
    post = get_object_or_404(Post.objects.select_related('author', 'category', 'location'), pk=post_id)

    # If the visitor is not the author, ensure the post is published and date passed — use published queryset
    if not (request.user.is_authenticated and request.user == post.author):
        published_qs = filter_and_annotate_posts(qs=Post.objects.filter(pk=post_id), include_published=True)
        post = get_object_or_404(published_qs)

    # ensure post has annotated comments_count (for consistent templates)
    if not hasattr(post, 'comments_count'):
        from django.db.models import Count
        post = Post.objects.filter(pk=post.pk).annotate(comments_count=Count('comments')).select_related('author', 'category', 'location').first()

    # prepare comment form and return
    comment_form = CommentForm()
    context = {'post': post, 'comment_form': comment_form}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(query_category(), slug=category_slug)
    posts = filter_and_annotate_posts(qs=category.posts.all(), include_published=True, order_by='-pub_date')
    page_obj = paginate_queryset(request, posts)
    context = {'category': category, 'post_list': page_obj}
    return render(request, 'blog/category.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated and request.user == user:
        # owner sees all own posts (including unpublished and future)
        posts_qs = user.posts.all()
        posts = filter_and_annotate_posts(qs=posts_qs, include_published=False, order_by='-pub_date')
    else:
        posts = filter_and_annotate_posts(author=user, include_published=True, order_by='-pub_date')
    page_obj = paginate_queryset(request, posts)
    context = {'profile_user': user, 'post_list': page_obj}
    return render(request, 'blog/profile.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    # reuse detail template for confirmation
    return render(request, 'blog/detail.html', {'post': post, 'confirm_delete': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post__pk=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/edit_comment.html', {'form': form, 'post': comment.post, 'comment': comment})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post__pk=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    # reuse post detail template for confirmation
    return render(request, 'blog/detail.html', {'post': comment.post, 'confirm_delete_comment': comment})


# error handlers
def register(request):
    from .forms import RegistrationForm
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/registration.html', {'form': form})


@login_required
def edit_profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect('blog:profile', username=username)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=username)
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'blog/edit_profile.html', {'form': form, 'profile_user': user})


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def handler404(request, exception):
    return render(request, 'pages/404.html', status=404)


def handler500(request):
    return render(request, 'pages/500.html', status=500)
