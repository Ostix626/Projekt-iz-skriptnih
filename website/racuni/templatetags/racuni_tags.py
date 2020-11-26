from django import template
register = template.Library()

@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    uk = qty * unit_price
    return round(uk,2)