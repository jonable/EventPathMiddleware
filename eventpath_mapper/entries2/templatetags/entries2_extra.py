
from django import template

register = template.Library()

@register.filter(name='getkey')
def getkey(value, arg):
    return value[arg]

@register.filter(name='getfloat')
def getfloat(value):
    return str(value)  

@register.filter(name='format_options')
def format_options(value):
	return "%s - %s" % (value[0], value[1])