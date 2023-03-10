from allianceauth import hooks
from fittings.app_settings import FITTINGS_AADISCORDBOT_INTEGRATION
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class FittingMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Fittings and Doctrines',
                              'far fa-list-alt fa-fw', 'fittings:dashboard',
                              navactive=['fittings:'])

    def render(self, request):
        if request.user.has_perm('fittings.access_fittings'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return FittingMenu()


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'fittings', '^fittings/')

@hooks.register('discord_cogs_hook')
def register_cogs():
    if FITTINGS_AADISCORDBOT_INTEGRATION is True:
        return ["fittings.cogs.fittings"]
    else:
        return [""]
