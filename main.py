import discord
from discord import Client
from discord.ext import commands, tasks
from discord.utils import find
import logging
import json
from tzlocal import get_localzone
import pytz
from datetime import *
from datetime import datetime
import asyncio
from translate import Translator
from collections.abc import Sequence
from itertools import cycle

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log',
                              encoding='utf-8',
                              mode='w')
handler.setFormatter(
    logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

prefix = "."
client = commands.Bot(description="Hackathon Bot", command_prefix=prefix)
client.remove_command("help")

status = cycle(['InterHacks', 'BeingLazy', 'StemWorlds', 'NapTime'])

# Variables

defaultC = 0
voiceChannel = 0


@client.event
async def on_ready():
    change_status.start()
    print(f"Bot has logged in as {client.user}")


@client.command()
async def help(ctx, args=None):
    help_embed = discord.Embed(title="Commands:",
                               description="List of every command by this bot",
                               color=discord.Color.blue())

    help_embed.add_field(
        name="Clearing",
        value=
        "clear - Clears the 5 latest messages \n clearall - Clears the whole channel \n clearmember (Member) - Clears a specific member \n clearself - Clears own messages",
        inline=False)
    help_embed.add_field(
        name="Timezone",
        value=
        "timezones - Displays avaliable timezones \n convertTZ (time, starting timezone, ending timezone) - Converts a time to a specific timezone",
        inline=False)
    help_embed.add_field(
        name="ID",
        value=
        "createID - Creates a shareable identity card \n loadID - Loads the identity card",
        inline=False)
    help_embed.add_field(
        name="Language",
        value=
        "translationlist - Shows all languages that can be translated between \n translate (targetlanguage, message) - Translates the message to the targetlanguage",
        inline=False)
    help_embed.add_field(
        name="Clock",
        value=
        "timer (time in minutes) - Sets a timer for X minutes \n remind (time in minutes, message, user) - Sends a timed message to an user",
        inline=False)
    help_embed.add_field(
        name="Misc",
        value=
        "export - Creates a txt file of all messages in a channel \n defaultchannel *Admin only - Sets default channel for bot messages \n editInfo *Admin only - Changes message shown on loadInfo \n info - Loads information set by Admin",
        inline=False)

    await ctx.send(embed=help_embed)


@tasks.loop(hours=6)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))


# Code to get all text channels


def getChannels(ctx):
    guild = ctx.guild
    text_channel_list = []
    for channel in guild.text_channels:
        text_channel_list.append(channel.name)
    return text_channel_list


# Change bot message sending channel


@client.command()
async def defaultchannel(ctx):
    global defaultC
    if ctx.message.author.guild_permissions.administrator:
        text_channel_list = getChannels(ctx)
        defaultC = text_channel_list.index(str(ctx.channel))

        embed = discord.Embed(
            title=
            f"{text_channel_list[defaultC]} is now default channel for bot messages"
        )
        await ctx.send(embed=embed)


# Code to send self.join message


@client.event
async def on_guild_join(ctx, guild):
    text_channel_list = getChannels(ctx)
    await text_channel_list[defaultC].send("InterHacksBot is ready")


# Code to dm a certain individual


@client.command()
async def DM(ctx, user: discord.User, *, message=None):
    message = message or "This Message is sent via DM"
    await user.send(message)


# mention member join


@client.event
async def on_member_join(member, guild, ctx):
    text_channel_list = getChannels(ctx)
    channel = discord.utils.get(ctx.guild.channels,
                                name=text_channel_list[defaultC])
    channel = client.get_channel(channel.id)
    await channel.send(f"{member.mention} has joined the server")


# mention member on leave


@client.event
async def on_member_remove(member, guild, ctx):
    text_channel_list = getChannels(ctx)
    channel = discord.utils.get(ctx.guild.channels,
                                name=text_channel_list[defaultC])
    channel = client.get_channel(channel.id)
    await channel.send(f"{member.mention} has left the server")


# clear


@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=2):
    await ctx.channel.purge(limit=amount)


@client.command()
@commands.has_permissions(manage_messages=True)
async def clearall(ctx):
    await ctx.channel.purge(limit=None)


@client.command()
@commands.has_permissions(manage_messages=True)
async def clearmember(ctx, member: discord.Member):
    messages = await ctx.history(limit=None).flatten()
    for message in messages:
        if message.author == member:
            await message.delete()


@client.command()
async def clearself(ctx):
    messages = await ctx.history(limit=None).flatten()
    for message in messages:
        if message.author == ctx.author:
            await message.delete()


# Export Messages


@client.command()
async def export(ctx):
    timezone = get_localzone()
    messages = await ctx.history(limit=None).flatten()
    export = open("Messages.txt", "w")
    export.write("Name - Time -> Message in decending order -> Attachments \n")
    for message in messages:
        convertedtime = timezone.fromutc(message.created_at)
        shortenedtime = str(convertedtime)[0:-13]
        if message.attachments:
            attachment = message.attachments[0]
            export.write(
                "%s\n" %
                f"{message.author} - {shortenedtime} -> {message.content} -> This message had an attachment named {attachment.filename}"
            )
        else:
            export.write(
                "%s\n" %
                f"{message.author} - {shortenedtime} -> {message.content}")

    with open("messages.txt", "rb") as export:
        await ctx.send("Exported Messages - ",
                       file=discord.File(export, "messages.txt"))


@client.command()
async def timer(ctx, t):
    try:
        otime = t
        t = int(t) * 60
        if t <= 0:
            await ctx.send("Negatives not allowed")
            raise BaseException

        message = await ctx.send(f"Timer: {t}")

        while True:
            t -= 1
            if t == 0:
                await message.edit(content=f"Timer for {otime} has ended")
                break

            await message.edit(content=f"Timer: {t}")
            await asyncio.sleep(1)
        await ctx.send(f"{ctx.author.mention} - Timer is up")
    except ValueError:
        await ctx.send("Need a number")


@client.command()
async def remind(ctx, time: int, message, user):
    await asyncio.sleep(time * 60)
    await ctx.send(f'{message}, {user}')


#Language translator


@client.command(aliases=['tr'])
async def translate(ctx, lang, *, args):

    lang = lang.lower()
    translator = Translator(to_lang=lang)
    final_text = translator.translate(args)
    # await ctx.send(final_text)

    embed = discord.Embed(title="Translated Results: ",
                          color=discord.Color.teal())

    embed.add_field(name=f"{lang.upper()} - ", value=f"{final_text}")

    await ctx.send(embed=embed)


@client.command()
async def translationlist(ctx):
    langlist = [
        'afrikaans',
        'albanian',
        'amharic',
        'arabic',
        'armenian',
        'azerbaijani',
        'basque',
        'belarusian',
        'bengali',
        'bosnian',
        'bulgarian',
        'catalan',
        'cebuano',
        'chichewa',
        'chinese (simplified)',
        'chinese (traditional)',
        'corsican',
        'croatian',
        'czech',
        'danish',
        'dutch',
        'english',
        'esperanto',
        'estonian',
        'filipino',
        'finnish',
        'french',
        'frisian',
        'galician',
        'georgian',
        'german',
        'greek',
        'gujarati',
        'haitian creole',
        'hausa',
        'hawaiian',
        'hebrew',
        'hebrew',
        'hindi',
        'hmong',
        'hungarian',
        'icelandic',
        'igbo',
        'indonesian',
        'italian',
        'japanese',
        'javanese',
        'kannada',
        'kazakh',
        'khmer',
        'korean',
        'kurdish (kurmanji)',
        'kyrgyz',
        'lao',
        'latin',
        'latvian',
        'lithuanian',
        'luxembourgish',
        'macedonian',
        'malagasy',
        'malay',
        'malayalam',
        'maltese',
        'maori',
        'marathi',
        'mongolian',
        'myanmar (burmese)',
        'nepali',
        'norwegian',
        'odia',
        'pashto',
        'persian',
        'polish',
    ]

    langlist2 = [
        'portuguese',
        'punjabi',
        'romanian',
        'russian',
        'samoan',
        'scots gaelic',
        'serbian',
        'sesotho',
        'shona',
        'sindhi',
        'sinhala',
        'slovak',
        'slovenian',
        'somali',
        'spanish',
        'sundanese',
        'swahili',
        'swedish',
        'tajik',
        'tamil',
        'telugu',
        'thai',
        'turkish',
        'ukrainian',
        'urdu',
        'uyghur',
        'uzbek',
        'vietnamese',
        'welsh',
        'xhosa',
        'yiddish',
        'yoruba',
        'zulu',
    ]

    print(langlist)
    print(langlist2)

    embed = discord.Embed(
        title="List of Languages",
        description="Use the 'translate' command to use these",
        colour=discord.Colour.teal())

    embed.add_field(name="Languages", value=langlist, inline=False)

    embed2 = discord.Embed(
        title="List of Languages continued",
        description="Use the 'translate' command to use these",
        colour=discord.Colour.teal())

    embed2.add_field(name="Continued languages", value=langlist2, inline=False)

    await ctx.send(embed=embed)
    await ctx.send(embed=embed2)


@client.command()
async def timezones(ctx):

    tzlst1 = [
        "Etc/GMT",
        "Etc/GMT+0",
        "Etc/GMT+1",
        "Etc/GMT+10",
        "Etc/GMT+11",
        "Etc/GMT+12",
        "Etc/GMT+2",
        "Etc/GMT+3",
        "Etc/GMT+4",
        "Etc/GMT+5",
        "Etc/GMT+6",
        "Etc/GMT+7",
        "Etc/GMT+8",
        "Etc/GMT+9",
        "Etc/GMT-0",
        "Etc/GMT-1",
        "Etc/GMT-10",
        "Etc/GMT-11",
        "Etc/GMT-12",
        "Etc/GMT-13",
        "Etc/GMT-14",
        "Etc/GMT-2",
        "Etc/GMT-3",
        "Etc/GMT-4",
        "Etc/GMT-5",
        "Etc/GMT-6",
        "Etc/GMT-7",
        "Etc/GMT-8",
        "Etc/GMT-9",
        "Etc/GMT0",
        "EST",
        "PST8PDT",
        "MST",
    ]

    embed = discord.Embed(
        title="List of Timezones",
        description="Use the 'convertTZ' command to use these",
        colour=discord.Colour.orange())

    embed.add_field(name="Timezones", value=tzlst1, inline=False)

    await ctx.send(embed=embed)


@client.command()
async def convertTZ(ctx, giventime, tz1, tz2):

    if giventime[-2:] == "AM" and giventime[:2] == "12":
        giventime = "00" + giventime[2:-2]

    elif giventime[-2:] == "AM":
        giventime = giventime[:-2]

    elif giventime[-2:] == "PM" and giventime[:2] == "12":
        giventime = giventime[:-2]

    else:
        giventime = str(int(giventime[:2]) + 12) + giventime[2:5]

    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.strptime(giventime, "%H:%M")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%r")

    # await ctx.send(dt)

    embed = discord.Embed(title="Converted Timezone: ",
                          color=discord.Color.purple())
    embed.add_field(name=f"{tz1} to {tz2}", value=f"{dt}", inline=False)

    await ctx.send(embed=embed)


def make_sequence(seq):
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return (seq, )


def message_check(channel=None,
                  author=None,
                  content=None,
                  ignore_bot=True,
                  lower=True):
    channel = make_sequence(channel)
    author = make_sequence(author)
    content = make_sequence(content)
    if lower:
        content = tuple(c.lower() for c in content)

    def check(message):
        if ignore_bot and message.author.bot:
            return False
        if channel and message.channel not in channel:
            return False
        if author and message.author not in author:
            return False
        actual_content = message.content.lower() if lower else message.content
        if content and actual_content not in content:
            return False
        return True

    return check


@client.command()
async def createID(ctx):

    userID = ctx.author.id
    user = ctx.author
    userinfo = []

    await user.send(
        f"This is InterHack bot collecting information to make your id card for {ctx.guild.name}"
    )
    await asyncio.sleep(5)

    await user.send(
        f"I will first need your name and pronouns in the fashion of - 'Joe Smith - He/Him' - Make sure to REPLY (use the arrow button) to each message to make your words count"
    )

    name = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    userinfo.append(name.content)

    await user.send(
        f"I will need your timezone - Make sure to REPLY (use the arrow button) to each message to make your words count"
    )

    tz = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    userinfo.append(tz.content)

    await user.send(
        f"Are you willing to work with other people from different timezones?")

    othertz = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    userinfo.append(othertz.content)

    await user.send(f"What are your computer science skills?")

    csskills = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    userinfo.append(csskills.content)

    await user.send(
        f"What is your level in computer science - Beginner, Intermediate, Advanced?"
    )

    cslevel = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    userinfo.append(cslevel.content)

    await user.send(f"what are your Hobbies?")

    hobbies = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    userinfo.append(hobbies.content)

    await user.send(
        f"Hackathon Experiences - New (1 - 2), Slightly Experienced (3 - 5), Experienced (5+)?"
    )

    hcexp = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    userinfo.append(hcexp.content)

    await user.send(f"What skill sets are you looking for in your teammates?")

    sst = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    userinfo.append(sst.content)

    await user.send(f"Other details?")

    od = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    userinfo.append(od.content)

    await user.send(f"Are you still looking for a teammate?")

    tm = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    userinfo.append(od.content)


    userinfoDictionary = {
        "name": userinfo[0],
        "tz": userinfo[1],
        "othertz": userinfo[2],
        "csskills": userinfo[3],
        "cslevel": userinfo[4],
        "hobbies": userinfo[5],
        "hackathon": userinfo[6],
        "otherskillset": userinfo[7],
        "od": userinfo[8],
        "tm" : userinfo[9]
    }

    jsonfile = open(f"{userID}.json", "w")
    jsonfile = json.dump(userinfoDictionary, jsonfile)


@client.command()
async def loadID(ctx):
    authorID = ctx.author.id

    jsonfile = open(f"{authorID}.json", "r")
    userinfoDictionary = json.load(jsonfile)

    print(userinfoDictionary)

    id = discord.Embed(title=f"information for {ctx.author}",
                       color=discord.Color.red())

    id.set_footer(icon_url=ctx.author.avatar_url,
                  text=f"Requested by {ctx.author.name}")

    id.add_field(name="Name", value=userinfoDictionary["name"], inline=True)
    id.add_field(name="Time Zone", value=userinfoDictionary["tz"], inline=True)
    id.add_field(name="Willing to work with other timezones",
                 value=userinfoDictionary["othertz"],
                 inline=False)
    id.add_field(name="CS Skill",
                 value=userinfoDictionary["csskills"],
                 inline=True)
    id.add_field(name="CS Level",
                 value=userinfoDictionary["cslevel"],
                 inline=True)
    id.add_field(name="Hobbies",
                 value=userinfoDictionary["hobbies"],
                 inline=False)
    id.add_field(name="Previous Experience with Hackathons",
                 value=userinfoDictionary["hackathon"],
                 inline=False)
    id.add_field(name="Expected Skill Sets from teammates",
                 value=userinfoDictionary["otherskillset"],
                 inline=False)
    id.add_field(name="Other details",
                 value=userinfoDictionary["od"],
                 inline=False)
    id.add_field(name="Still looking for a team",
                 value=userinfoDictionary["tm"],
                 inline=False)

    await ctx.send(embed=id)


@client.command()
async def editInfo(ctx):
    if ctx.message.author.guild_permissions.administrator:
        guildID = ctx.guild.id
        user = ctx.author
        guildinfo = []

    await user.send(
        f"This is InterHack bot collecting information to make your info card for {ctx.guild.name}"
    )

    await asyncio.sleep(5)

    await user.send(
        f"Reply (using arrow) to this message with your information regarding your hackathon - You can include details like date and time, timezones for these events, schedules, and even prizes"
    )

    info = await client.wait_for(
        'message', check=message_check(channel=ctx.author.dm_channel))
    guildinfo.append(info.content)

    guildinfoDictionary = {"info": guildinfo[0]}

    jsonfile = open(f"{guildID}.json", "w")
    jsonfile = json.dump(guildinfoDictionary, jsonfile)


@client.command()
async def info(ctx):
    guildID = ctx.guild.id

    jsonfile = open(f"{guildID}.json", "r")
    guildinfoDictionary = json.load(jsonfile)

    guildid = discord.Embed(title=f"Information for {ctx.guild}",
                            color=discord.Color.green())

    guildid.set_footer(icon_url=ctx.author.avatar_url,
                       text=f"Requested by {ctx.author.name}")

    guildid.add_field(name="___",
                      value=guildinfoDictionary["info"],
                      inline=False)

    await ctx.send(embed=guildid)

# with open("token.txt", "r") as token:
#     token = token.readline()

# client.run(token)

