from django.template.defaulttags import register
from django.utils.safestring import mark_safe


@register.filter()
def get_item(dict_, key):
    return dict_.get(key)

@register.filter(name='empty_slots')
def empty_slots(fittings: dict, slot_type: str):
    keys = fittings.keys()

    for key in keys:
        if slot_type in key:
            # This slot type is not empty
            return False
    # This slot type is completely empty
    return True


@register.filter
def break_html_lines(value):
    return value.replace("<br>", "\n").replace("<br />", "\n")

