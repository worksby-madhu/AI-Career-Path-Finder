from django import template

register = template.Library()


@register.filter
def lookup(values, index):
    """Safely retrieve a list item by numeric index in a template."""
    try:
        return values[int(index)]
    except (TypeError, ValueError, IndexError):
        return ""
