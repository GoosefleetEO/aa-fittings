# Cog used by https://github.com/pvyParts/allianceauth-discordbot

# Cog Stuff
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color

# AA Contexts
from aadiscordbot.cogs.utils.decorators import sender_has_perm
from aadiscordbot.app_settings import get_site_url
from django.core.exceptions import ObjectDoesNotExist

from fittings.models import Fitting, Doctrine, Category
from django.db.models import Q


import re

import logging
logger = logging.getLogger('aadiscordbot.cogs.fittings')


class Fittings(commands.Cog):
    """
    A Cog to respond to AA Fittings Links
    Includes more information as the Discord Embed for AA is of limited Use
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    @sender_has_perm('fitting.access_fittings')
    async def respond_to_fittings(self, message):
        """
        Listens to ALL Messages, act if they contain AA-Fittings Links
        """
        logger.debug(f"Fittings Cog: Message Received {message.content}")
        pattern = re.compile(r".*\/(fittings)\/(doctrine|fit|cat)\/(\d+)\/")

        if re.search(get_site_url(), message.content) is not None:
            fit_tuples = re.findall(pattern, message.content)
        else:
            logger.debug("Fittings Cog: No Match")
            return

        if len(fit_tuples) > 0:
            await message.edit(suppress=True)
            await message.channel.trigger_typing()
            await message.add_reaction(chr(0x231B))
            logger.debug(f"Fittings Cog: Message Match {message.content}")

            for fit_tuple in fit_tuples:
                if fit_tuple[0] == "fittings":
                    if fit_tuple[1] == "fit":
                        logger.debug(f"Fittings Cog: Fit Detected {fit_tuple[2]}")
                        embed = fitting_details(fit_tuple[2])
                    elif fit_tuple[1] == "doctrine":
                        logger.debug(f"Fittings Cog: Doctrine Detected {fit_tuple[2]}")
                        embed = doctrine_details(fit_tuple[2])
                    elif fit_tuple[1] == "cat":
                        logger.debug(f"Fittings Cog: Category Detected {fit_tuple[2]}")
                        embed = category_details(fit_tuple[2])
                    else:
                        await message.reply("I Detected a fitting link, but not a valid page. Please notify an Admin", mention_author=False)
                await message.reply(embed=embed, mention_author=False)
            await message.clear_reaction(chr(0x231B))
        else:
            logger.debug("Fittings Cog: No Match")
            return

    @commands.command(pass_context=True)
    @sender_has_perm('fitting.access_fittings')
    async def fit(self, ctx, fit_name):
        """
        Returns fits and ships matching the string given
        """
        await ctx.channel.trigger_typing()
        await ctx.message.add_reaction(chr(0x231B))

        try:
            fits = Fitting.objects.filter(Q(name__icontains=fit_name) | Q(ship_type__type_name__icontains=fit_name))
        except ObjectDoesNotExist:
            return await ctx.reply("No Fits Found", mention_author=False)

        for fit in fits:
            embed = fitting_details(fit.id)
            await ctx.reply(embed=embed, mention_author=False)

        return await ctx.message.clear_reaction(chr(0x231B))

    @commands.command(pass_context=True)
    @sender_has_perm('fitting.access_fittings')
    async def fit_id(self, ctx, fit_id):
        """
        Return information on a fit ID
        """

        embed = fitting_details(fit_id)

        return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(pass_context=True)
    @sender_has_perm('fitting.access_fittings')
    async def fit_ship(self, ctx, fit_id):
        """
        Returns fittings for a Ship Type
        """

        embed = fitting_details(fit_id)

        return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(pass_context=True)
    @sender_has_perm('fitting.access_fittings')
    async def doctrine(self, ctx, doctrine_name):
        """
        Returns doctrines matching the string given
        """
        await ctx.channel.trigger_typing()
        await ctx.message.add_reaction(chr(0x231B))

        try:
            doctrines = Doctrine.objects.filter(name__icontains=doctrine_name)
        except ObjectDoesNotExist:
            return await ctx.reply("No Doctrine Found", mention_author=False)

        for doctrine in doctrines:
            embed = doctrine_details(doctrine.id)
            await ctx.reply(embed=embed, mention_author=False)

        return await ctx.message.clear_reaction(chr(0x231B))

    @commands.command(pass_context=True)
    @sender_has_perm('fitting.access_fittings')
    async def doctrine_id(self, ctx, doctrine_id):
        """
        Return information on a doctrine ID
        """

        embed = doctrine_details(doctrine_id)

        return await ctx.reply(embed=embed, mention_author=False)

    @commands.command(pass_context=True)
    @sender_has_perm('fitting.access_fittings')
    async def category_id(self, ctx, category_id):
        """
        Return information on a category ID
        """

        embed = category_details(category_id)

        return await ctx.reply(embed=embed, mention_author=False)


def fitting_details(fit_id):
    try:
        fit = Fitting.objects.get(id=fit_id)
    except ObjectDoesNotExist:
        embed = Embed(title="Fitting Not Found")
        return

    embed = Embed(title=f"{fit.ship_type.type_name}: {fit.name}")
    embed.set_thumbnail(
        url=f"https://images.evetech.net/types/{fit.ship_type_type_id}/render?size=128"
    )
    embed.description = fit.description

    doctrines_value = ''
    for doctrine in Doctrine.objects.filter(fittings=fit).values("name", "id"):
        doctrines_value = f"{doctrines_value}[{doctrine['name']}]({get_site_url()}/fittings/doctrine/{doctrine['id']}/) "
    if doctrines_value == '':
        doctrines_value = 'None'

    category_value = ''
    for category in Category.objects.filter(fittings=fit).values("name", "id"):
        category_value = f"{category_value}[{category['name']}]({get_site_url()}/fittings/cat/{category['id']}/) "
    if category_value == '':
        category_value = 'None'

    embed.add_field(
        name="Doctrines:",
        value=doctrines_value
    )
    embed.add_field(
        name="Categories",
        value=category_value
    )
    embed.add_field(
        name="URL",
        value=f"{get_site_url()}/fittings/fit/{fit_id}/",
        inline=False
    )
    return embed


def doctrine_details(doctrine_id):
    try:
        doctrine = Doctrine.objects.get(id=doctrine_id)
    except ObjectDoesNotExist:
        embed = Embed(title="Doctrine Not Found")
        return embed

    embed = Embed(title=doctrine.name)
    embed.set_thumbnail(
        url=doctrine.icon_url
    )
    embed.description = doctrine.description

    for fit in doctrine.fittings.all():
        embed.add_field(
            name=fit.ship_type.type_name,
            value=f"[{fit.name}]({get_site_url()}/fittings/fit/{fit.id}/)"
        )

    embed.add_field(
        name="URL",
        value=f"{get_site_url()}/fittings/doctrine/{doctrine_id}/",
        inline=False
    )

    return embed


def category_details(category_id):
    try:
        category = Category.objects.get(id=category_id)
    except ObjectDoesNotExist:
        embed = Embed(title="Category Not Found")
        return embed

    embed = Embed(title=category.name)

    for doctrine in category.doctrines.all():
        embed.add_field(
            name=doctrine.name,
            value=f"[{doctrine.name}]({get_site_url()}/fittings/doctrine/{doctrine.id}/)"
        )
    embed.add_field(
        name="URL",
        value=f"{get_site_url()}/fittings/cat/{category_id}/",
        inline=False
    )

    return embed


def setup(bot):
    bot.add_cog(Fittings(bot))
