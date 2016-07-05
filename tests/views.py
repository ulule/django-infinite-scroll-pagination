import json

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from infinite_scroll_pagination.paginator import SeekPaginator, EmptyPage

from .models import Article, ArticleCustomPK


def pagination_ajax(request, pk=None, custom_pk=False):
    if not request.is_ajax():
        return Http404()

    if pk is not None:
        date = get_object_or_404(Article, pk=pk).date
    else:
        date = None

    if not custom_pk:
        articles = Article.objects.all()
    else:
        articles = ArticleCustomPK.objects.all()

    paginator = SeekPaginator(articles, per_page=20, lookup_field='date')

    try:
        page = paginator.page(value=date, pk=pk)
    except EmptyPage:
        return Http404()

    articles_list = [{'title': a.title} for a in page]

    data = {
        'articles': articles_list,
        'has_next': page.has_next(),
    }

    if not custom_pk:
        data['pk'] = page[-1].pk

    return HttpResponse(json.dumps(data), content_type='application/json')


def pagination_ajax_custom_pk(request, pk=None):
    return pagination_ajax(request=request, pk=pk, custom_pk=True)
