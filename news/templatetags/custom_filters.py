from django import template


register = template.Library()

UNWANTED_WORDS = ['плохо', 'bad', 'good', 'worse', 'Lorem', 'lorem']


@register.filter()
def censor(value):
    list_values = value.split(" ")
    new_str = ""
    for i in list_values:
        if i in UNWANTED_WORDS:
            new_str += f'{"*"*(len(i) - 2)}{i[-2]}{i[-1]} '
        else:
            new_str += i + " "

    return new_str
