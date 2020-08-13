from django.template.defaulttags import register
from django.utils.safestring import mark_safe


@register.filter()
def get_item(dict_, key):
    return dict_.get(key)


@register.simple_tag()
def item_img_circle(_id, name, size):
    return mark_safe('<img class="img-circle" src="https://imageserver.eveonline.com/Type/%s_128.png"'
                     ' style="height: %spx; width: %spx;" title="%s">' % (_id, size, size, name))


@register.simple_tag()
def item_img(_id, name, size):
    return mark_safe('<img src="https://imageserver.eveonline.com/Type/%s_128.png"'
                     ' style="height: %spx; width: %spx;" title="%s">' % (_id, size, size, name))


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

