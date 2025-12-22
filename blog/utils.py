from django.utils import timezone
from django.db.models import Count

from blog.models import Category, Post


def query_category():
    """Return published categories."""
    return Category.objects.filter(is_published=True)


def base_post_queryset():
    """Base queryset for posts with select_related applied."""
    return Post.objects.select_related('category', 'location', 'author')


def filter_and_annotate_posts(qs=None, include_published=True, author=None, order_by='-pub_date'):
    """
    Apply published filter (by pub_date and is_published and category), annotate with comments_count,
    and apply ordering. If include_published is False, no published filtering is applied.
    If qs is None, uses full Post queryset.
    """
    if qs is None:
        qs = base_post_queryset()

    if include_published:
        now = timezone.now()
        qs = qs.filter(pub_date__lte=now, is_published=True, category__is_published=True)

    if author is not None:
        qs = qs.filter(author=author)

    qs = qs.annotate(comments_count=Count('comments'))

    if order_by:
        qs = qs.order_by(order_by)

    return qs


def paginate_queryset(request, queryset, per_page=10):
    """Return paginator page object for queryset."""
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
