from django.core.paginator import Paginator


def get_page(paginator_qs, request, per_page=10):
    return Paginator(paginator_qs, per_page).get_page(request.GET.get('page'))
