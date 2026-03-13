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


@register.filter
def format_step_value(value):
    """Format step value for display: URLs as links, lists of URLs as link list"""
    from django.utils.safestring import mark_safe
    from django.utils.html import escape
    if value is None or value == '':
        return ''
    if isinstance(value, list):
        parts = []
        for v in value:
            v = str(v).strip()
            if v.startswith('http://') or v.startswith('https://'):
                parts.append(f'<a href="{escape(v)}" target="_blank" rel="noopener" class="text-blue-400 hover:text-blue-300 underline">View file</a>')
            else:
                parts.append(escape(v))
        return mark_safe(' &middot; '.join(parts))
    s = str(value)
    if s.startswith('http://') or s.startswith('https://'):
        return mark_safe(f'<a href="{escape(s)}" target="_blank" rel="noopener" class="text-blue-400 hover:text-blue-300 underline">View / Open link</a>')
    return escape(s)

