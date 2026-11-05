from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from blog.forms import CommentForm, PostCreateForm
from blog.models import Post, Category, Comment, User
from blog.paginator import get_page


def get_posts(posts=Post.objects, published=True,
              select_related=('category', 'location', 'author'),
              annotate_with={'comment_count': Count('comments')}):
    """Фильтр по опубликованным."""
    if published:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    if select_related:
        posts = posts.select_related(*select_related)
    if annotate_with:
        posts = posts.annotate(**annotate_with)
    if posts.model._meta.ordering:
        posts = posts.order_by(*posts.model._meta.ordering)
    return posts


def index(request):
    return render(request, 'blog/index.html', {
        'page_obj': get_page(get_posts(), request)
    })


def post_detail(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=post_id)
        if post.author == request.user:
            return render(request, 'blog/detail.html', {
                'post': post,
                'form': CommentForm(),
                'comments': post.comments.select_related('author')
            })

    post = get_object_or_404(
        Post,
        pk=post_id,
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    )

    return render(request, 'blog/detail.html', {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.select_related('author')
    })


def category_posts(request, category_slug):
    category_obj = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    return render(request, 'blog/category.html', {
        'category': category_obj,
        'page_obj': get_page(
            get_posts(category_obj.posts),
            request
        )
    })


@login_required
def create_post(request):
    form = PostCreateForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, 'blog/create.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('blog:profile', request.user.username)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id)
    form = PostCreateForm(
        request.POST or None, request.FILES or None, instance=post
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post.id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', request.user.username)
    form = PostCreateForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)

    return render(request, 'blog/profile.html', {
        'profile': author,
        'page_obj': get_page(
            get_posts(
                author.posts,
                published=request.user != author
            ),
            request
        )
    })


@login_required
def edit_profile(request, username):
    form = UserChangeForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:profile', request.user.username)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', post_id)
    comments = post.comments.select_related('author')
    return render(request, 'blog/detail.html', {
        'post': post, 'form': form, 'comments': comments
    })


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment.objects.select_related('post'),
        pk=comment_id,
    )

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', {
        'form': form,
        'post': comment.post,
        'comments': comment.post.comments.select_related('author'),
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment, pk=comment_id
    )

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id)

    if request.method != 'POST':
        return render(
            request,
            'blog/delete_comment.html',
            {'comment': comment}
        )
    comment.delete()
    return redirect('blog:post_detail', post_id)
