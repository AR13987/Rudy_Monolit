from django import template

register = template.Library()

@register.filter(name='percent_of')
# Вычисление процента part от whole:
def percent_of(part, whole):
  try:
    return 100 * float(part) / whole
  except (ZeroDivisionError, TypeError):
    return 0