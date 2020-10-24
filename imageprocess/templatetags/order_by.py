from django import template

register = template.Library()

@register.simple_tag(name='lowPrice')
def lowPrice(list1):
    lotte = list1.order_by('lottePrice')
    paginator = Paginator(lotte,3)
    page = request.GET.get('page')
    lotteposts = paginator.get_page(page)
    return lotteposts
    