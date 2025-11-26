from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary and isinstance(dictionary, dict):
        return dictionary.get(key, {})
    return {}

@register.filter
def replace(value, arg):
    """Replace characters in string. Usage: {{ value|replace:"old|new" }}"""
    if not value:
        return value
    try:
        old, new = arg.split('|', 1)
        return str(value).replace(old, new)
    except (ValueError, AttributeError):
        return value

