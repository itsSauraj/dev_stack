from django import template

register = template.Library()

@register.filter
def times(number):
    return range(number)

@register.filter
def add(value, arg):
    try:
        return value + arg
    except (ValueError, TypeError):
        return value
    
@register.filter
def create_for(value):
    list = [item.lower() for item in value.split(" ")]
    return "id_" + "_".join(list)