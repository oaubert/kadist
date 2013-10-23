from django import template

TAG_MAXCOUNT = 14
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
    elif c < TAG_MINCOUNT:
        return TAG_MINSIZE
    else:
        return long(TAG_MINSIZE + TAG_FACTOR * (c - TAG_MINCOUNT))

@register.filter
def similarity_index(s):
    return int(s * 10)

@register.filter
def similar(work, p):
    return work.similar(p)

def callMethod(obj, methodName):
    method = getattr(obj, methodName)
    if obj.__dict__.has_key("__callArg"):
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()

def args(obj, arg):
    if not obj.__dict__.has_key("__callArg"):
        obj.__callArg = []
    obj.__callArg += [arg]
    return obj

register.filter("call", callMethod)
register.filter("args", args)
