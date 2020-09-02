import datetime
import json

from django import template
register = template.Library()

state_colours = {
    "failure": "firebrick",
    "success": "darkgreen",
    "stale": "gainsboro"
}


@register.filter(name="expiration")
def expiration(value):
    return value + datetime.timedelta(days=90)


@register.filter(name="doughnut")
def doughnut(queryset):
    # This is a terrible hack
    labels = []
    data = []
    colours = []
    for row in queryset:
        for k, v in row.items():
            if k.endswith('__count'):
                data.append(v)
            else:
                labels.append(v)
                colours.append(state_colours.get(v, 'black'))

    result = {'labels': labels, 'datasets': [{'data': data, 'backgroundColor': colours}]}
    return json.dumps(result)
