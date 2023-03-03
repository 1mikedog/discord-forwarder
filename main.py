import os
import platform
import random
import time

from discord.ext import commands
from discord import Webhook, RequestsWebhookAdapter
from urlextract import URLExtract
import requests
import discord

import pickle
import asyncio
import config
is_windows = "windows" in platform.system().lower()

bot = commands.Bot(command_prefix='zcxvzxcvzxcvxvcxv')
affiliate_tag = config.affiliate_tag

extractor = URLExtract()

from urllib.parse import urlparse, urlunparse


def amazonify(url, affiliate_tag):
    """Generate an Amazon affiliate link given any Amazon link and affiliate
    tag.

    :param str url: The Amazon URL.
    :param str affiliate_tag: Your unique Amazon affiliate tag.
    :rtype: str or None
    :returns: An equivalent Amazon URL with the desired affiliate tag included,
        or None if the URL is invalid.

    Usage::

        >>> from amazonify import amazonify
        >>> url = 'someamazonurl'
        >>> tag = 'youraffiliatetag'
        >>> print amazonify(url, tag)
        ...
    """
    # Ensure the URL we're getting is valid:
    new_url = urlparse(url)
    if not new_url.netloc:
        return None

    # Replace the original querystrings with our affiliate tag. Since all
    # Amazon querystrings have no useful purpose, we can safely remove them and
    # only add our affiliate tag.
    new_url = new_url[:4] + ('tag=%s' % affiliate_tag,) + new_url[5:]

    return urlunparse(new_url)

def amazonify_string(str):
    try:
        print("start amazonify  string")
        urls = extractor.find_urls(str)
        my_list = []
        for u in urls:
            print(u)
            if "xxxxxxx dealsaurus" in u:
                print("DEALSAURUS")
                splits = u.split("?link=")
                my_list.append([splits[0] + "?link=", ""])
                u = splits[1]
                print("NEW: {}".format(u))

            if "amazon.com" in u or "amzn.to" in u:
                my_list.append([u, amazonify(u, affiliate_tag)])
            if "t.co" in u:
                session = requests.Session()  # so connections are recycled
                resp = session.head(u, allow_redirects=True, timeout=10)
                new_link = resp.url
                if "fkd.sale" in new_link:
                    new_new_link = new_link.split("=")[1]
                    session = requests.Session()  # so connections are recycled
                    resp = session.head(new_new_link, allow_redirects=True, timeout=10)
                    final_link = resp.url
                    if "amazon.com" in final_link or "amzn.to" in final_link:
                        my_list.append([u, amazonify(final_link, affiliate_tag)])
                elif "amazon.com" in new_link or "amzn.to" in new_link:
                    my_list.append([u, amazonify(new_link, affiliate_tag)])

        for ml in my_list:
            str = str.replace(ml[0], ml[1])
        print("end amazonify string")
        return str
    except:
        print("TIMED OUT...")
        return str


@bot.event
async def on_ready():
    print("READY!")

@bot.event
async def on_message(message):
    chan_id = message.channel.id
    if message.author.bot:
        pass
    else:
        return
    for entry in config.channels_to_forward:
        if entry[0] == chan_id:
            print("MESSAGE IN #{} in {}".format(message.channel.name, message.channel.guild.name))
            embed = None
            try:
                embed = message.embeds[0]
                embed.url = amazonify_string(embed.url)
                embed.description = amazonify_string(embed.description)

                c = 0
                for field in embed.fields:
                    embed.set_field_at(0, field.name, amazonify_string(field.value))
                    c += 1

                print("found an embed")
            except:
                print("no embed!!")

            try:
                webhook = Webhook.from_url(entry[1], adapter=RequestsWebhookAdapter())
                webhook.send(content=message.content + " " + "<@&{}>".format(entry[2]), embed=embed)
            except Exception as e:
                print("==%%==")
                print(str(e))


bot.run(config.USER_TOKEN)