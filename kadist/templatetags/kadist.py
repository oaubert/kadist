from django import template

TAG_MAXCOUNT = 50
TAG_MINCOUNT = 0
TAG_MINSIZE = 10
TAG_MAXSIZE = 48
TAG_FACTOR = 1. * (TAG_MAXSIZE - TAG_MINSIZE) / (TAG_MAXCOUNT - TAG_MINCOUNT)

register = template.Library()

@register.filter
def tagsize(c):
    """Return the size in points for a given tag count.
    """
    if c > TAG_MAXCOUNT:
        return TAG_MAXSIZE
    elif c < TAG_MINSIZE:
        return TAG_MINSIZE
    else:
        return long(TAG_MINSIZE + TAG_FACTOR * (c - TAG_MINCOUNT))

