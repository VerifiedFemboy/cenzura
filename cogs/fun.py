"""
Copyright 2022-2024 PoligonTeam

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import femcord.femcord as femcord
from femcord.femcord import commands, types, InvalidArgument, HTTPException
from femcord.femcord.http import Route
from femcord.femcord.permissions import Permissions
from femcord.femcord.enums import Intents
from femcord.femcord.utils import get_index
from aiohttp import ClientSession
from bs4 import BeautifulSoup, ResultSet
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pyfiglet import Figlet
from typing import Union
from utils import *
import io, random, urllib.parse, json, re

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.garfield_emojis = {"0": "1072691610254585927", "1": "1072691612578234438", "2": "1072691613802954753", "3": "1072691615610712235",
                                "4": "1072691617829494905", "5": "1072691620245413938", "6": "1072691622573248642", "7": "1072691624158695476",
                                "8": "1072691627149238282", "9": "1072691628713717760", "a": "930949124151443546", "b": "930949123870429286",
                                "c": "930949123836895312", "d": "930949123757203457", "e": "930949123866263572", "f": "930949124172419152",
                                "g": "930949124017238027", "h": "930949124050808892", "i": "930949124046590032", "j": "930949123719430196",
                                "k": "930949124147277894", "l": "930949124008849408", "m": "930949124835131402", "n": "930949124235362344",
                                "o": "930949124008865882", "p": "930949123706880014", "q": "930949125426528357", "r": "930949124336021564",
                                "s": "930949124226961408", "t": "930949123966898207", "u": "930949124466032740", "v": "930949124046590033",
                                "w": "930949123866263573", "x": "930949124105334795", "y": "930949124172419153", "z": "930949124046594049",
                                " ": "930949124138889236"}
        self.public_flags_emojis = {"DISCORD_EMPLOYEE": "933476948343144508", "PARTNERED_SERVER_OWNER": "933476948246675506",
                                    "HYPESQUAD_EVENTS": "933476948234096661", "BUG_HUNTER_LEVEL_1": "933476948225687623",
                                    "BRAVERY": "933476948234096660", "BRILLIANCE": "933476948389294170", "BALANCE": "933476948292796427",
                                    "EARLY_SUPPORTER": "933476948338966578", "BUG_HUNTER_LEVEL_2": "933476948276019220",
                                    "VERIFIED_BOT_DEVELOPER": "933476948594790460", "CERTIFIED_MODERATOR": "933476947915333633",
                                    "ACTIVE_DEVELOPER": "1040346532144238652"}
        self.APPLICATION_COMMAND_BADGE = "1072689600658673734"
        self.status_emojis = {"ONLINE": "977693019279077399", "IDLE": "977693019321028649", "DND": "977693019430076456",
                              "INVISIBLE": "977693019518160916", "OFFLINE": "977693019518160916", "MOBILEONLINE": "1002296215456714953",
                              "MOBILEIDLE": "1002296213913214976", "MOBILEDND": "1002296212503932988"}
        self.results = {}
        self.urls = {}

    @commands.command(description="User avatar", usage="[user]")
    async def avatar(self, ctx: commands.Context, user: types.User = None):
        user = user or ctx.author
        image = await self.bot.http.session.get(user.avatar_url)

        await ctx.reply(files=[("avatar." + ("gif" if user.avatar[:2] == "a_" else "png"), await image.content.read())])

    @commands.command(description="Shows the percentage of love between users", usage="(user) [user]", aliases=["love"])
    async def ship(self, ctx: commands.Context, user: types.User, user2: types.User = None):
        user2 = user2 or ctx.author

        user_avatar_response = await self.bot.http.session.get(user.avatar_as("png"))
        user2_avatar_response = await self.bot.http.session.get(user2.avatar_as("png"))

        user_avatar = io.BytesIO(await user_avatar_response.content.read())
        user2_avatar = io.BytesIO(await user2_avatar_response.content.read())

        ship_image = Image.open("./assets/images/ship.jpg").convert("RGBA")

        user_image = Image.open(user_avatar).convert("RGBA")
        user2_image = Image.open(user2_avatar).convert("RGBA")

        user_image = ImageOps.fit(user_image, (300, 300))
        user2_image = ImageOps.fit(user2_image, (300, 300))

        ship_image.paste(user_image, (360, 250), user_image)
        ship_image.paste(user2_image, (890, 180), user2_image)

        image = io.BytesIO()
        ship_image.save(image, "PNG")

        percent = get_int(user, user2)

        await ctx.reply(f"**{user.username}** + **{user2.username}** = **{user.username[:len(user.username) // 2].lower()}{user2.username[len(user2.username) // 2:].lower()}**\nThey love each other for **{percent}%**!", files=[("ship.png", image.getvalue())])

    @commands.command(description="dog", aliases=["ars", "6vz", "piesvz", "<@338075554937044994>", "<@!338075554937044994>"])
    async def dog(self, ctx: commands.Context):
        alias = ctx.message.content.split()[0][len((await self.bot.get_prefix(self.bot, ctx.message))[-1]):]

        if alias in ("6vz", "piesvz", "<@338075554937044994>", "<@!338075554937044994>"):
            return await ctx.reply(files=[("dog.png", open("./assets/images/6vz.png", "rb")), ("dog2.png", open("./assets/images/6vz2.png", "rb"))])
        elif alias == "ars":
            return await ctx.reply(files=[("dog.jpg", open("./assets/images/ars.jpg", "rb"))])

        response = await self.bot.http.session.get("https://some-random-api.ml/img/dog")
        response_data = await response.json()
        image = await self.bot.http.session.get(response_data["link"])
        content = await image.content.read()

        try:
            mimetype = femcord.utils.get_mime(content)
        except InvalidArgument:
            return await self.dog(ctx)

        extension = mimetype.split("/")[1]

        await ctx.reply(files=[("dog." + extension, content)])

    @commands.command(description="cat", aliases=["mesik", "<@563718132863074324>", "<@!563718132863074324>"])
    async def cat(self, ctx: commands.Context):
        alias = ctx.message.content.split()[0][len((await self.bot.get_prefix(self.bot, ctx.message))[-1]):]

        if alias in ("mesik", "<@563718132863074324>", "<@!563718132863074324>"):
            return await ctx.reply(files=[("cat.jpg", open("./assets/images/mesik.jpg", "rb")), ("cat2.png", open("./assets/images/mesik2.jpg", "rb"))])

        image = await self.bot.http.session.get("https://cataas.com/cat" + ("/gif" if random.random() > .5 else ""))
        content = await image.content.read()

        try:
            mimetype = femcord.utils.get_mime(content)
        except InvalidArgument:
            return await self.cat(ctx)

        extension = mimetype.split("/")[1]

        await ctx.reply(files=[("cat." + extension, content)])

    @commands.command(description=".i.", usage="(text)", aliases=["ascii"])
    async def figlet(self, ctx: commands.Context, *, text):
        figlet = Figlet().renderText("\n".join(text.split()))

        if text[:3] == ".i." and (not text[4:] or text[4:].isdigit()):
            figlet = figlet.splitlines()[:6]
            num = int(text[4:]) if text[4:] else 3
            if num > 100:
                num = 100
            for _ in range(num):
                figlet.insert(3, figlet[2])
            figlet = "\n".join(figlet)

        await ctx.reply("```" + figlet + "```")

    @commands.command(description="gay", usage="[user]")
    async def howgay(self, ctx: commands.Context, user: types.User = None):
        user = user or ctx.author

        y = get_int(user)
        x = get_int(user, self.bot.gateway.bot_user)

        await ctx.reply("https://charts.idrlabs.com/graphic/sexual-orientation?p=%d,%d&l=PL" % (y, x))

    @commands.command(description="Achievement Get!", usage="(text)")
    async def achievement(self, ctx: commands.Context, *, text: replace_chars):
        if len(text) > 23:
            return await ctx.reply(f"Provided text is too long (`{len(text)}/23`)")

        image = await self.bot.http.session.get(f"https://minecraftskinstealer.com/achievement/{random.randint(1, 40)}/Achievement+Get%21/{text}")

        await ctx.reply(files=[("achievement.png", await image.content.read())])

    @commands.command(description="Replaces text with garfield emojis", usage="(text)")
    async def garfield(self, ctx: commands.Context, *, text: replace_chars):
        if len(text) > 60:
            return await ctx.reply(f"Provided text is too long (`{len(text)}`/`60`)")

        garfield_text = ""

        for char in text:
            char = char.lower()
            if char in self.garfield_emojis:
                garfield_text += f"<:garfield_{'space' if char == ' ' else char}:{self.garfield_emojis[char]}>"
                continue

            garfield_text += char

        await ctx.reply(garfield_text)

    @commands.command(description="Adds a hidden message to text", usage="(text) | (hidden_text)", other={"embed": femcord.Embed().set_image(url="https://cdn.poligon.lgbt/riEyNGVIuO.png")})
    async def encode(self, ctx: commands.Context, *, text: replace_chars):
        text = text.split(" | ")
        text[1] = text[1].replace(" ", "_")

        if 2 > len(text):
            return await ctx.reply("You did not provide the hidden text")

        if len(text[0]) < 2:
            return await ctx.reply(f"Provided text is too short (`{len(text[0])}/2`)")

        await ctx.reply(text[0][0] + encode_text(text[1]) + text[0][1:])

    @commands.command(description="Reveals the hidden message from text", usage="(text)", other={"embed": femcord.Embed().set_image(url="https://cdn.poligon.lgbt/fsdKWwqWKx.png")})
    async def decode(self, ctx: commands.Context, *, text):
        allowed_chars = [group[0] for group in CHARS] + [SEPARATOR]
        new_text = ""

        for char in text:
            if char in allowed_chars:
                new_text += char

        await ctx.reply(decode_text(new_text))

    # @commands.Listener
    # async def on_interaction_create(self, interaction):
    #     if ("calc", interaction.member.user.id, interaction.channel.id, interaction.message.id) in self.interactions:
    #         if not interaction.message.id in self.results:
    #             self.results[interaction.message.id] = ["", 0]

    #         if self.results[interaction.message.id][0] == "KABOOM!":
    #             self.results[interaction.message.id][0] = ""

    #         match interaction.data.custom_id:
    #             case "leftbracket":
    #                 self.results[interaction.message.id][0] += "("
    #                 self.results[interaction.message.id][1] = 0
    #             case "rightbracket":
    #                 self.results[interaction.message.id][0] += ")"
    #                 self.results[interaction.message.id][1] = 0
    #             case "power":
    #                 self.results[interaction.message.id][0] += "**"
    #                 self.results[interaction.message.id][1] = 0
    #             case "modulo":
    #                 self.results[interaction.message.id][0] += "%"
    #                 self.results[interaction.message.id][1] = 0
    #             case "backspace":
    #                 self.results[interaction.message.id][0] = self.results[interaction.message.id][0][:-1]
    #                 self.results[interaction.message.id][1] = 0
    #             case "clear":
    #                 self.results[interaction.message.id][0] = ""
    #                 self.results[interaction.message.id][1] = 0
    #             case "divide":
    #                 self.results[interaction.message.id][0] += "/"
    #                 self.results[interaction.message.id][1] = 0
    #             case "multiply":
    #                 self.results[interaction.message.id][0] += "*"
    #                 self.results[interaction.message.id][1] = 0
    #             case "minus":
    #                 self.results[interaction.message.id][0] += "-"
    #                 self.results[interaction.message.id][1] = 0
    #             case "dot":
    #                 self.results[interaction.message.id][0] += "."
    #                 self.results[interaction.message.id][1] = 0
    #             case "equal":
    #                 if len(self.results[interaction.message.id][0]) <= 50:
    #                     try:
    #                         self.results[interaction.message.id][0] += "=" + str(round(eval(self.results[interaction.message.id][0]), 2))
    #                     except:
    #                         self.results[interaction.message.id][0] = "KABOOM!" if self.results[interaction.message.id][0] == "/0" else ""
    #                     self.results[interaction.message.id][1] = 0
    #             case "add":
    #                 self.results[interaction.message.id][0] += "+"
    #                 self.results[interaction.message.id][1] = 0
    #             case "0":
    #                 if not self.results[interaction.message.id][0] == "0" and not len(self.results[interaction.message.id][0]) == 1:
    #                     self.results[interaction.message.id][0] += "0"
    #                     self.results[interaction.message.id][1] = 0
    #             case _:
    #                 if self.results[interaction.message.id][1] <= 5:
    #                     self.results[interaction.message.id][0] += interaction.data.custom_id
    #                     self.results[interaction.message.id][1] += 1

    #         await interaction.callback(lib.InteractionCallbackTypes.UPDATE_MESSAGE, "```" + (self.results[interaction.message.id][0] if self.results[interaction.message.id][0] else "0") + "```")

    #         if "=" in self.results[interaction.message.id][0]:
    #             self.results[interaction.message.id][0] = ""

    # @commands.command(description="liczydło", aliases=["kalkulator", "calculator"], enabled=False)
    # async def calc(self, ctx: commands.Context):
    #     components = lib.Components(
    #         lib.Row(
    #             lib.Button("x\u02b8", style=lib.ButtonStyles.SECONDARY, custom_id="power"),
    #             lib.Button("%", style=lib.ButtonStyles.SECONDARY, custom_id="modulo"),
    #             lib.Button("<-", style=lib.ButtonStyles.SECONDARY, custom_id="backspace"),
    #             lib.Button("C", style=lib.ButtonStyles.DANGER, custom_id="clear")
    #         ),
    #         lib.Row(
    #             lib.Button("7", style=lib.ButtonStyles.SECONDARY, custom_id="7"),
    #             lib.Button("8", style=lib.ButtonStyles.SECONDARY, custom_id="8"),
    #             lib.Button("9", style=lib.ButtonStyles.SECONDARY, custom_id="9"),
    #             lib.Button("/", style=lib.ButtonStyles.SECONDARY, custom_id="divide"),
    #             lib.Button("(", style=lib.ButtonStyles.SECONDARY, custom_id="leftbracket")
    #         ),
    #         lib.Row(
    #             lib.Button("4", style=lib.ButtonStyles.SECONDARY, custom_id="4"),
    #             lib.Button("5", style=lib.ButtonStyles.SECONDARY, custom_id="5"),
    #             lib.Button("6", style=lib.ButtonStyles.SECONDARY, custom_id="6"),
    #             lib.Button("*", style=lib.ButtonStyles.SECONDARY, custom_id="multiply"),
    #             lib.Button(")", style=lib.ButtonStyles.SECONDARY, custom_id="rightbracket")
    #         ),
    #         lib.Row(
    #             lib.Button("1", style=lib.ButtonStyles.SECONDARY, custom_id="1"),
    #             lib.Button("2", style=lib.ButtonStyles.SECONDARY, custom_id="2"),
    #             lib.Button("3", style=lib.ButtonStyles.SECONDARY, custom_id="3"),
    #             lib.Button("-", style=lib.ButtonStyles.SECONDARY, custom_id="minus")
    #         ),
    #         lib.Row(
    #             lib.Button("0", style=lib.ButtonStyles.SECONDARY, custom_id="0"),
    #             lib.Button(".", style=lib.ButtonStyles.SECONDARY, custom_id="dot"),
    #             lib.Button("=", style=lib.ButtonStyles.PRIMARY, custom_id="equal"),
    #             lib.Button("+", style=lib.ButtonStyles.SECONDARY, custom_id="add")
    #         )
    #     )

    #     message = await ctx.reply("```0```", components=components)
    #     self.interactions.append(("calc", ctx.author.id, ctx.channel.id, message.id))

    @commands.command(description="inside joke", usage="[user/text/image]")
    async def cantseeme(self, ctx: commands.Context, *, arg: Union[types.User, str] = None):
        arg = arg or ctx.author

        if ctx.message.attachments:
            image = await self.bot.http.session.get(ctx.message.attachments[0].url)
            arg = io.BytesIO(await image.content.read())

        if isinstance(arg, types.User):
            image = await self.bot.http.session.get(arg.avatar_url)
            arg = io.BytesIO(await image.content.read())

        bush = Image.open("./assets/images/bush.png")

        if isinstance(arg, str):
            if len(arg) > 105:
                 return await ctx.reply(f"Provided text is too long (`{len(arg)}/105`)")

            if len(arg) > 15:
                arg = "\n".join(arg[x:x+15] for x in range(0, len(arg), 15))

            draw = ImageDraw.Draw(bush)
            font = ImageFont.truetype("./assets/fonts/HKNova-Medium.ttf", 30)

            draw.text((round(bush.size[0] / 2) - 50, round(bush.size[1] / 2) - 60), arg, font=font)
        else:
            arg = Image.open(arg)
            width, height = arg.size

            width = 150 if width > 150 else width
            height = 150 if height > 150 else height

            arg.thumbnail((width, height))

            bush.paste(arg, (round(bush.size[0] / 2 - arg.size[0] / 2), round(bush.size[1] / 2 - arg.size[1] / 2 - 30)))

        image = io.BytesIO()
        bush.save(image, "PNG")

        await ctx.reply(files=[("cantseeme.png", image.getvalue())])

    @commands.command(description="lgbt", usage="[user]", aliases=["lgbt"])
    async def gay(self, ctx: commands.Context, user: types.User = None):
        user = user or ctx.author

        image = await self.bot.http.session.get(user.avatar_url)
        image = io.BytesIO(await image.content.read())

        lgbt = Image.open("./assets/images/lgbt.png")
        image = Image.open(image)

        lgbt = ImageOps.fit(lgbt, (512, 512))
        image = ImageOps.fit(image, (512, 512))

        mask = Image.new("L", (512, 512), 128)

        avatar = Image.composite(image, lgbt, mask)
        image = io.BytesIO()

        avatar.save(image, "PNG")

        await ctx.reply(files=[("gay.png", image.getvalue())])

    @commands.command(description="Random meme from jbzd", aliases=["mem"])
    @commands.is_nsfw
    async def meme(self, ctx: commands.Context):
        memes = []

        while not memes:
            memes_page = await self.bot.http.session.get(f"https://jbzd.com.pl/str/{random.randint(1, 235)}")
            memes_soup = BeautifulSoup(await memes_page.content.read(), "lxml")

            memes = memes_soup.find_all("img", {"class": "article-image"})

        await ctx.reply(random.choice(memes)["src"])

    @commands.command(description="\U0001F633", usage="[user]")
    async def dick(self, ctx: commands.Context, user: types.User = None):
        await self.figlet(ctx, text=f".i. {get_int(user or ctx.author) // 5}")

    # @commands.command(description="taobao, aliexpress, and china", usage="(product)", aliases=["aliexpress"])
    # async def taobao(self, ctx: commands.Context, *, product):
    #     response = await self.bot.http.session.get("https://pl.aliexpress.com/wholesale?SearchText=" + urllib.parse.quote_plus(product))
    #     soup = BeautifulSoup(await response.content.read(), "lxml")

    #     raw_item_list = soup.find_all("script", {"type": "text/javascript"})[3].string.splitlines()[3].strip("window.runParams = ")[:-1]
    #     item_list = json.loads(raw_item_list)["mods"]["itemList"]["content"]

    #     random_product = random.choice(item_list)

    #     await ctx.reply(f"\"{random_product['title']['displayTitle']}\"\nhttps://aliexpress.com/item/{random_product['productId']}.html\n\n*from aliexpress.com*")

    # @commands.command(description="shopee wyszukiwarka", usage="(produkt)", aliases=["shopenis", "fakeali", "alisexpress"])
    # async def shopee(self, ctx: commands.Context, *, product):
    #     response = (await (await self.bot.http.session.get("https://shopee.pl/api/v4/search/search_items?by=relevancy&keyword=" + urllib.parse.quote_plus(product) + "&limit=60&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2")).json())["items"]

    #     if len(response) == 0:
    #         return await ctx.reply("Nie ma takiego produktu :cry:")

    #     random_product = random.choice(response)['item_basic']

    #     embed = femcord.Embed(title=f"{str(format(random_product['price'] / 100000, '.2f'))}PLN | {random_product['name']}", url=f"https://shopee.pl/{random_product['name'].replace(' ', '-')}-i.{random_product['shopid']}.{random_product['itemid']}")
    #     embed.set_thumbnail(url=f"https://cf.shopee.pl/file/{random_product['image']}")
    #     embed.set_author(name="shopee.pl")
    #     embed.set_footer(text="Your preferred online shopping platform.")

    #     await ctx.reply(f"\"{random_product['name']}\"\nhttps://shopee.pl/{random_product['name'].replace(' ', '-')}-i.{random_product['shopid']}.{random_product['itemid']} *z shopee.pl*", embed=embed)

    @commands.command(description="Random wallpaper from tapetus.pl", aliases=["tapeta"])
    async def tapetus(self, ctx: commands.Context):
        response = await self.bot.http.session.get(f"https://tapetus.pl/,st_{random.randint(0, 5527)}.php")
        soup = BeautifulSoup(await response.content.read(), "lxml")

        images = soup.find_all("img", {"class": "img_srednie"})
        image = random.choice(images).parent

        await ctx.reply("https://tapetus.pl/obrazki/n/" + image["href"][:-3].replace(",", "_") + "jpg")

    @commands.command(description="Shows information about user", usage="[user]", aliases=["ui", "user", "cotozacwel", "kimtykurwajestes"])
    async def userinfo(self, ctx: commands.Context, user: Union[types.Member, types.User] = None):
        user = user or ctx.member

        if isinstance(user, types.Member):
            member = user
            user = member.user

        elif isinstance(user, types.User):
            member = None

        color = self.bot.embed_color

        if member is not None:
            if member.hoisted_role is not None:
                color = member.hoisted_role.color

        embed = femcord.Embed(title=f"Information about {user.global_name or user.username}:", color=color)
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name="ID:", value=user.id)
        embed.add_field(name="Username:", value=user.username)
        if member is not None:
            if member.nick is not None:
                embed.add_field(name="Nickname:", value=member.nick)
            if member.roles[1:]:
                embed.add_field(name="Roles:", value=" ".join(types.m @ role for role in member.roles[1:]))
            if member.presence:
                text = ""
                client_status = member.presence.client_status
                if client_status.desktop:
                    desktop_status = client_status.desktop.name
                    text += f"<:{desktop_status}:{self.status_emojis[desktop_status]}>"
                if client_status.mobile:
                    mobile_status = client_status.mobile.name
                    text += f"<:MOBILE{mobile_status}:{self.status_emojis['MOBILE' + mobile_status]}>"
                for activity in member.presence.activities:
                    if activity.type is femcord.ActivityTypes.CUSTOM:
                        text += " "
                        if activity.emoji and not activity.emoji.id:
                            text += activity.emoji.name + " "
                        if activity.state:
                            text += activity.state
                        break
                if text:
                    embed.add_field(name="Status:", value=text)
            embed.add_field(name="Date joined:", value=f"{femcord.types.t @ member.joined_at} ({femcord.types.t['R'] @ member.joined_at})")
        embed.add_field(name="Date created:", value=f"{femcord.types.t @ user.created_at} ({femcord.types.t['R'] @ user.created_at})")
        if user.public_flags:
            embed.add_field(name="Badges:", value=" ".join(f"<:{flag.name}:{self.public_flags_emojis[flag.name]}>" for flag in user.public_flags if flag.name in self.public_flags_emojis))
        embed.add_field(name="Avatar:", value=f"[link]({user.avatar_url})")
        if user.bot is True:
            link = f"https://discord.com/oauth2/authorize?client_id={user.id}&permissions=0&scope=bot"

            try:
                data = await self.bot.http.request(Route("GET", "applications", user.id, "rpc"))
            except femcord.errors.HTTPException:
                data = {"flags": 0, "description": None}

            intents = []

            if data["flags"] & 1 << 12:
                intents.append(Intents.GUILD_PRESENCES)
            if data["flags"] & 1 << 14:
                intents.append(Intents.GUILD_MEMBERS)
            if data["flags"] & 1 << 18:
                intents.append(Intents.GUILD_MESSAGES)
            if data["flags"] & 1 << 23:
                embed.add_field(name="Badges:", value=f"<:APPLICATION_COMMAND_BADGE:{self.APPLICATION_COMMAND_BADGE}>")

            if data["description"]:
                embed.description = data["description"]
            if "guild_id" in data:
                try:
                    guild_data = await self.bot.http.request(Route("GET", "guilds", data["guild_id"], "widget.json"))

                    if "code" not in guild_data:
                        embed.add_field(name="Guild:", value=f"{guild_data['name']} ({guild_data['id']})")
                except femcord.errors.HTTPException:
                    pass
            if "terms_of_service_url" in data:
                embed.add_field(name="ToS:", value=data["terms_of_service_url"])
            if "privacy_policy_url" in data:
                embed.add_field(name="Privacy Policy:", value=data["privacy_policy_url"])
            if "tags" in data:
                embed.add_field(name="Tags:", value=", ".join(data["tags"]))
            if intents:
                embed.add_field(name="Intents:", value=", ".join([intent.name for intent in intents]))
            if "install_params" in data:
                embed.add_field(name="Permissions:", value=", ".join([permission.name for permission in Permissions.from_int(int(data["install_params"]["permissions"])).permissions]))
                link = f"https://discord.com/oauth2/authorize?client_id={user.id}&permissions={data['install_params']['permissions']}&scope={'%20'.join(data['install_params']['scopes'])}"

        args = []
        kwargs = {}

        if member is not None:
            args.append(types.m @ user)
        if user.bot is True:
            kwargs["components"] = femcord.Components(femcord.Row(femcord.Button("Invite bot", url=link)))

        await ctx.reply(*args, embed=embed, **kwargs)

    @commands.command(description="Shows information about the guild", aliases=["si"])
    async def serverinfo(self, ctx: commands.Context):
        embed = femcord.Embed(title=f"Information about {ctx.guild.name}:", color=self.bot.embed_color)
        embed.set_thumbnail(url=ctx.guild.icon_url)

        embed.add_field(name="Owner:", value=types.m @ ctx.guild.owner)
        embed.add_field(name="ID:", value=ctx.guild.id)
        embed.add_field(name="Users:", value=len(ctx.guild.members), inline=True)
        embed.add_field(name="Channels:", value=len(ctx.guild.channels), inline=True)
        embed.add_field(name="Roles:", value=len(ctx.guild.roles), inline=True)
        embed.add_field(name="Emojis:", value=len(ctx.guild.emojis), inline=True)
        embed.add_field(name="Stickers:", value=len(ctx.guild.stickers), inline=True)
        embed.add_blank_field()
        embed.add_field(name="Date created:", value=f"{femcord.types.t @ ctx.guild.created_at} ({femcord.types.t['R'] @ ctx.guild.created_at})")
        embed.add_field(name="Boosts:", value=ctx.guild.premium_subscription_count, inline=True)
        embed.add_field(name="Level:", value=ctx.guild.premium_tier, inline=True)
        embed.add_blank_field()
        if ctx.guild.vanity_url is not None:
            embed.add_field(name="Custom url:", value="discord.gg/" + ctx.guild.vanity_url, inline=ctx.guild.banner is None)
        embed.add_field(name="Icon:", value=f"[link]({ctx.guild.icon_url})", inline=True)
        if ctx.guild.banner is not None:
            embed.add_field(name="Banner:", value=f"[link]({ctx.guild.banner_url})", inline=True)
            embed.set_image(url=ctx.guild.banner_url)
            embed.add_blank_field()

        await ctx.reply(embed=embed)

    @commands.command(description="Shows information about invite", usage="(invite)", aliases=["ii"])
    async def inviteinfo(self, ctx: commands.Context, invite):
        invite = invite.split("/")[-1]

        try:
            data = await self.bot.http.request(Route("GET", "invites", invite + "?with_counts=true"))
            guild = data["guild"]
        except HTTPException:
            return await ctx.reply("This invite does not exists")

        embed = femcord.Embed(title=f"Information about {invite}:", color=self.bot.embed_color)

        embed.add_field(name="ID:", value=guild["id"])
        embed.add_field(name="Name:", value=guild["name"])
        if guild["description"] is not None:
            embed.add_field(name="Description:", value=guild["description"])
        embed.add_field(name="Boosts:", value=guild["premium_subscription_count"])
        if guild["nsfw_level"] > 0:
            embed.add_field(name="NSFW Level:", value=guild["nsfw_level"])
        embed.add_field(name="Approximate member count:", value=data["approximate_member_count"])
        if guild["icon"] is not None:
            embed.set_thumbnail(url=f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png")
            embed.add_field(name="Icon:", value=f"[link](https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png)", inline=True)
        if guild["banner"] is not None:
            embed.set_image(url=f"https://cdn.discordapp.com/banners/{guild['id']}/{guild['banner']}.png")
            embed.add_field(name="Banner:", value=f"[link](https://cdn.discordapp.com/banners/{guild['id']}/{guild['banner']}.png)", inline=True)
        if guild["splash"] is not None:
            embed.add_field(name="Splash:", value=f"[link](https://cdn.discordapp.com/splashes/{guild['id']}/{guild['splash']}.png)", inline=True)

        await ctx.reply(embed=embed)

    @commands.command(description="Information about TruckersMP account", usage="(name)", aliases=["tmp", "ets2", "ets"], other={"embed": femcord.Embed(description="\nName: `steamid64`, `steam name`")})
    async def truckersmp(self, ctx: commands.Context, *, _id):
        if not re.match(r"^\d+$", _id):
            response = await self.bot.http.session.get("https://steamcommunity.com/id/" + _id, headers={"User-Agent": self.bot.user_agent})

            try:
                soup = BeautifulSoup(await response.content.read(), "lxml")
                _id = json.loads(soup.find_all("script", {"type": "text/javascript"}, text=re.compile("g_rgProfileData"))[0].string.splitlines()[1][20:-1])["steamid"]
            except json.decoder.JSONDecodeError:
                return await ctx.reply("No such steam account was found")

        response = await self.bot.http.session.get("https://api.truckersmp.com/v2/player/" + _id)
        response = await response.json()

        if response["error"]:
            return await ctx.reply("No such TruckersMP account was found")

        response = response["response"]

        embed = femcord.Embed(title=f"Informacje o {response['name']}:", color=self.bot.embed_color)
        embed.set_thumbnail(url=response["avatar"])
        embed.add_field(name="ID:", value=response["id"])
        embed.add_field(name="Steam64 ID:", value=response["steamID64"])
        embed.add_field(name="Nick:", value=response["name"])
        embed.add_field(name="Created date:", value=femcord.types.t @ datetime.strptime(response["joinDate"], "%Y-%m-%d %H:%M:%S"))
        if response["banned"]:
            embed.add_field(name="Banned:", value="Yes")
        if response["patreon"]["isPatron"]:
            embed.add_field(name="Patreon support:", value="Yes")
        if response["vtc"]["inVTC"]:
            embed.add_field(name="Company name:", value=response["vtc"]["name"])
            embed.add_field(name="Company tags:", value=response["vtc"]["tag"])

        await ctx.reply(embed=embed)

    async def fetch(self, word, url, tag, attributes, expression):
        response = await self.bot.http.session.get(url, headers={"user-agent": self.bot.user_agent})

        soup = BeautifulSoup(await response.content.read(), "lxml")
        text = soup.find_all(tag, attributes)

        if text is None:
            return "No such word was found"

        text = text[0].get_text()

        return f"**{word}**\n{re.findall(expression, text)[-1]}\n*z <{url.replace(' ', '%20')}>*"

    @commands.group(description="Dictionary", aliases=["definition", "word", "dict", "def"])
    async def dictionary(self, ctx: commands.Context):
        cog = self.bot.get_cog("Help")
        embed = cog.get_help_embed(ctx.command)

        await ctx.reply(embed=embed)

    @dictionary.command(usage="(word)", aliases=["pl"])
    async def polish(self, ctx: commands.Context, *, word):
        await ctx.reply(await self.fetch(word, "https://sjp.pwn.pl/szukaj/" + word + ".html", "div", {"class": "znacz"}, r"[\w,. ]+"))

    @dictionary.command(usage="(word)", aliases=["en"])
    async def english(self, ctx: commands.Context, *, word):
        await ctx.reply(await self.fetch(word, "https://dictionary.cambridge.org/pl/dictionary/english/" + word, "div", {"class": "def"}, r"[\w,. ]+"))

    @dictionary.command(usage="(word)", aliases=["es"])
    async def spanish(self, ctx: commands.Context, *, word):
        await ctx.reply(await self.fetch(word, "https://dictionary.cambridge.org/pl/dictionary/spanish-english/" + word, "div", {"class": "def"}, r"[\w,. ]+"))

    @dictionary.command(usage="(word)")
    @commands.is_nsfw
    async def urban(self, ctx: commands.Context, *, word):
        await ctx.reply(await self.fetch(word, "https://www.urbandictionary.com/define.php?term=" + word, "div", {"class": "meaning"}, r".+"))

    @commands.command(description="Information about meme from KnowYourMeme", usage="(name)", aliases=["kym", "meme"])
    @commands.is_nsfw
    async def knowyourmeme(self, ctx: commands.Context, *, name):
        async with ClientSession() as session:
            async with session.get(f"http://rkgk.api.searchify.com/v1/indexes/kym_production/instantlinks?query={name}&field=name&fetch=name%2Curl&function=10&len=1") as response:
                data = await response.json()

                if not data["results"]:
                    return await ctx.reply("No such meme was found")

                async with session.get("https://knowyourmeme.com" + data["results"][0]["url"]) as response:
                    content = await response.content.read()

                    soup = BeautifulSoup(content, "lxml")
                    text: ResultSet = soup.find_all("section", {"class": "bodycopy"})[0]
                    about = text.find("h2", {"id": "about"}).find_next("p").get_text()

                    await ctx.reply(f"**Information about {urllib.parse.unquote(data['results'][0]['name'])}**\n\n{about}\n\n*z <https://knowyourmeme.com{data['results'][0]['url']}>*")

    @commands.command(description="Information about gihub account", usage="(user_name)", aliases=["gh"])
    async def github(self, ctx: commands.Context, *, name):
        async with ClientSession() as session:
            async with session.get(f"https://api.github.com/users/{name}") as response:
                if not response.status == 200:
                    return await ctx.reply("No such github account was found")

                data = await response.json()

                embed = femcord.Embed(title=f"Information about {data['login']}:", color=self.bot.embed_color)
                embed.add_field(name="ID:", value=data["id"], inline=True)
                embed.add_field(name="Name:", value=data["name"], inline=True)
                embed.add_blank_field()
                if data["avatar_url"]:
                    embed.set_thumbnail(url=data["avatar_url"])
                embed.add_field(name="Followers count:", value=data["followers"], inline=True)
                embed.add_field(name="Following count:", value=data["following"], inline=True)
                embed.add_blank_field()
                embed.add_field(name="Public repositories count:", value=data["public_repos"], inline=True)
                embed.add_field(name="Public gists count:", value=data["public_gists"], inline=True)
                embed.add_blank_field()
                embed.add_field(name="Created date:", value=femcord.types.t @ datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%SZ"), inline=True)
                embed.add_field(name="Last update:", value=femcord.types.t @ datetime.strptime(data["updated_at"], "%Y-%m-%dT%H:%M:%SZ"), inline=True)
                embed.add_blank_field()
                if data["bio"]:
                    embed.add_field(name="Bio:", value=data["bio"])

                await ctx.reply(embed=embed)

    @commands.command(description="guess who it is")
    async def who(self, ctx: commands.Context):
        members = []

        members_with_pfp = [member for member in ctx.guild.members if member.user.avatar]

        if len(members_with_pfp) < 10:
            return await ctx.reply("There is not enough users with avatar on this server")

        while not len(members) == 10:
            member = random.choice(members_with_pfp)

            if not member in members:
                members.append(member)

        correct = random.choice(members)

        color = self.bot.embed_color

        if correct.hoisted_role is not None:
            color = correct.hoisted_role.color

        embed = femcord.Embed(title="Guess who it is:", color=color)
        embed.set_image(url=correct.user.avatar_url)

        def get_components():
            return femcord.Components(
                femcord.Row(
                    femcord.SelectMenu(
                        custom_id = "members",
                        placeholder = "Choose a member",
                        options = [
                            femcord.Option(member.user.username, member.user.id) for member in members
                        ]
                    )
                )
            )

        message = await ctx.reply(embed=embed, components=get_components())

        async def on_select(interaction):
            nonlocal members

            selected_member = members[get_index(members, interaction.data.values[0], key=lambda member: member.user.id)]

            if selected_member == correct:
                return await interaction.callback(femcord.InteractionCallbackTypes.UPDATE_MESSAGE, f"{types.m @ interaction.member} guessed!", embeds=[], components={})
            elif len(members) == 4:
                return await interaction.callback(femcord.InteractionCallbackTypes.UPDATE_MESSAGE, "No one guessed", embeds=[], components={})
            else:
                members.remove(selected_member)
                await interaction.callback(femcord.InteractionCallbackTypes.UPDATE_MESSAGE, embed=embed, components=get_components())
                await self.bot.wait_for("interaction_create", on_select, lambda interaction: interaction.channel.id == ctx.channel.id and interaction.message.id == message.id, timeout=60 * 5, on_timeout=on_timeout)

        async def on_timeout():
            await message.edit("No one guessed", embeds=[], components=[])

        await self.bot.wait_for("interaction_create", on_select, lambda interaction: interaction.channel.id == ctx.channel.id and interaction.message.id == message.id, timeout=60 * 5, on_timeout=on_timeout)

    @commands.command(description="Random nickname")
    async def nick(self, ctx):
        await ctx.reply(get_random_username())

def setup(bot: commands.Bot) -> None:
    bot.load_cog(Fun(bot))