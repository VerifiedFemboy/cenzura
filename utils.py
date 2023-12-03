"""
Copyright 2022 PoligonTeam

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

import femcord
from femcord import types
from aiohttp import ClientSession, ClientTimeout
from models import Artists, Guilds, LastFM, Lyrics
from config import LASTFM_API_URL, LASTFM_API_KEY
from lastfm import Client, Track, exceptions
from lyrics import GeniusClient, MusixmatchClient, TrackNotFound, LyricsNotFound, Lyrics as LyricsTrack
import asyncio, config, random, json

class fg:
    black = "\u001b[30m"
    red = "\u001b[31m"
    green = "\u001b[32m"
    yellow = "\u001b[33m"
    blue = "\u001b[34m"
    magenta = "\u001b[35m"
    cyan = "\u001b[36m"
    white = "\u001b[37m"
    reset = "\u001b[0m"

class bg:
    black = "\u001b[40m"
    red = "\u001b[41m"
    green = "\u001b[42m"
    yellow = "\u001b[43m"
    blue = "\u001b[44m"
    magenta = "\u001b[45m"
    cyan = "\u001b[46m"
    white = "\u001b[47m"
    reset = "\u001b[0m"

CHARS = (("\u200b", ("0", "1", "2", "3")), ("\u200c", ("4", "5", "6", "7")), ("\u200d", ("8", "9", "A", "B")), ("\u200e", ("C", "D", "E", "F")))
SEPARATOR = "\u200f"

def encode_text(text):
    return "".join(CHARS[int(char, 16) // 4][0] * ((int(char, 16) % 4) + 1) + SEPARATOR for char in "%X" % int("".join(("0" * (7 - len(f"{ord(char):b}")) + f"{ord(char):b}" for char in text)), 2))

def decode_text(text):
    return [binary := f"{int(''.join([group[1] for group in CHARS if group[0] == chars[0]][0][int(len(chars) - 1)] for chars in text.split(SEPARATOR)[:-1]), 16):b}", "".join(chr(int(binary[i:i+7], 2)) for i in range(0, len(binary), 7))][1]

def replace_chars(text):
    to_replace = [("ą", "a"), ("ś", "s"), ("ó", "o"), ("ł", "l"), ("ę", "e"), ("ń", "n"), ("ź", "z"), ("ż", "z"), ("ć", "c")]

    for x, y in to_replace:
        text = text.replace(x, y)

    return text

def get_random_username():
    gender = random.randint(0, 1)

    with open("NIGGER/words%d.txt" % gender, "r") as f:
        word = random.choice(f.read().splitlines())

    with open("NIGGER/names%d.txt" % gender, "r") as f:
        name = random.choice(f.read().splitlines()).replace(" ", "_").lower()

    return f"{word}_{name}{random.randint(1, 100)}"

async def update_lastfm_avatars():
    async def get_lastfm_avatar(lastfm_user: LastFM):
        async with ClientSession() as session:
            async with session.get(LASTFM_API_URL + f"?method=user.getinfo&user={user.username}&api_key={LASTFM_API_KEY}&format=json") as response:
                data = await response.json()

                if not "image" in data:
                    return

                elif data["image"][-1] == lastfm_user.avatar:
                    return

                await LastFM.filter(id=lastfm_user.id).update(avatar=data["image"][-1])

    users = LastFM.all()

    for user in await users:
        asyncio.create_task(get_lastfm_avatar(user))

async def get_artist_image(artist: str):
    artist_db = await Artists.filter(artist=artist).first()

    if artist_db:
        return artist_db.image

    async with Client() as client:
        try:
            image = await client.artist_image(artist)
        except exceptions.NotFound:
            return "https://www.last.fm/static/images/marvin.05ccf89325af.png"

        await Artists.create(artist=artist, image=image)

    return await get_artist_image(artist)

async def get_track_lyrics(artist: str, title: str, session: ClientSession):
    lyrics_db = await Lyrics.get_or_none(title__icontains=title)

    if lyrics_db is None:
        name = artist + " " + title
        track = LyricsTrack(artist, title)

        async with MusixmatchClient(config.MUSIXMATCH, session) as musixmatch:
            try:
                track = await musixmatch.get_lyrics(name)
                source = "Musixmatch"
            except (TrackNotFound, LyricsNotFound):
                pass

            if track.lyrics is None:
                async with GeniusClient(config.GENIUS, session) as genius:
                    try:
                        track = await genius.get_lyrics(name)
                        source = "Genius"
                    except (TrackNotFound, LyricsNotFound):
                        return None

            lyrics_db = await Lyrics.get_or_none(title__icontains=track.title)

            if lyrics_db is None:
                lyrics_db = Lyrics(artist=track.artist, title=track.title, source=source, lyrics=track.lyrics)
                await lyrics_db.save()

    return lyrics_db

def convert(**items):
    objects = {
        types.Guild: lambda guild: dict(
            id = guild.id,
            name = guild.name,
            description = guild.description or False,
            icon_url = guild.icon_url or False,
            banner_url = guild.banner_url or False,
            owner = dict(
                id = guild.owner.user.id,
                username = guild.owner.user.username,
                avatar_url = guild.owner.user.avatar_url or False,
                bot = guild.owner.user.bot
            ),
            members = len(guild.members),
            channels = len(guild.channels),
            roles = len(guild.roles),
            emojis = len(guild.emojis),
            stickers = len(guild.stickers)
        ),
        types.Channel: lambda channel: dict(
            id = channel.id,
            name = channel.name,
            topic = channel.topic or False,
            nsfw = channel.nsfw,
            position = channel.position
        ),
        types.Role: lambda role: dict(
            id = role.id,
            name = role.name,
            color = role.color,
            hoist = role.hoist,
            mentionable = role.mentionable,
            position = role.position
        ),
        types.User: lambda user: dict(
            id = user.id,
            username = user.username,
            avatar_url = user.avatar_url,
            bot = user.bot or False
        ),
        Track: lambda track: dict(
            artist = dict(
                name = track.artist.name,
                url = track.artist.url,
                image = [
                    dict(
                        url = image.url,
                        size = image.size
                    ) for image in track.artist.image
                ],
                streamable = track.artist.streamable,
                on_tour = track.artist.on_tour or False,
                stats = dict(
                    listeners = track.artist.stats.listeners,
                    playcount = track.artist.stats.playcount,
                    userplaycount = track.artist.stats.userplaycount
                ),
                similar = [
                    dict(
                        name = similar.name,
                        url = similar.url,
                        image = [
                            dict(
                                url = image.url,
                                size = image.size
                            ) for image in similar.image
                        ]
                    ) for similar in track.artist.similar
                ],
                tags = [
                    dict(
                        name = tag.name,
                        url = tag.url
                    )
                    for tag in track.artist.tags
                ],
                bio = dict(
                    links = dict(
                        name = track.artist.bio.links.name,
                        rel = track.artist.bio.links.rel,
                        url = track.artist.bio.links.url
                    ),
                    published = track.artist.bio.published,
                    summary = track.artist.bio.summary,
                    content = track.artist.bio.content
                )
            ),
            image = [
                dict(
                    url = image.url,
                    size = image.size
                ) for image in track.image
            ] if track.image else [],
            album = dict(
                name = track.album.name or False,
                mbid = track.album.mbid or False,
                image = [
                    dict(
                        url = image.url,
                        size = image.size
                    ) for image in track.image
                ] if track.image else [],
                position = track.album.position or False
            ) if track.album else False,
            title = track.title,
            url = track.url,
            date = dict(
                uts = track.date.uts,
                text = track.date.text,
                date = track.date.date
            ) if track.date else False,
            listeners = track.listeners,
            playcount = track.playcount,
            scrobbles = track.scrobbles,
            tags = [
                dict(
                    name = tag.name,
                    url = tag.url
                )
                for tag in track.tags
            ]
        )
    }

    converted = {}

    for key, value in items.items():
        if (_type := type(value)) in objects:
            converted[key] = objects[type(value)](value)
        elif _type is list:
            converted[key] = [objects[type(item)](item) for item in value]

    return converted

def get_int(user, user2 = None):
    user2 = user2 or user

    user_avatar = user.avatar
    user2_avatar = user2.avatar

    if user_avatar is None:
        user_avatar = "".join(chr(int(char)) for char in str(int(user.created_at.timestamp())))
    if user2_avatar is None:
        user2_avatar = "".join(chr(int(char)) for char in str(int(user2.created_at.timestamp())))

    return (int(user.id) + int(user2.id)) * sum(ord(a) + ord(b) for a, b in list(zip(user_avatar, user2_avatar))) % 10000 // 100

def table(names, rows):
    text = ""
    spaces = max([len(str(name)) for name in names] + [len(str(value)) for row in rows for value in row]) + 1

    text += "\n+" + ("-" * (spaces + 1) + "+") * len(names) + "\n"
    text += "|"

    for name in names:
        text += " " + name + " " * (spaces - len(name)) + "|"

    text += "\n+" + ("-" * (spaces + 1) + "+") * len(names) + "\n"

    for row in rows:
        text += "|"
        for value in row:
            text += " " + str(value) + " " * (spaces - len(str(value))) + "|"
        text += "\n"

    text += "+" + ("-" * (spaces + 1) + "+") * len(names) + "\n"

    return text

async def request(method: str, url: str, *, headers: dict = None, cookies: dict = None, data: dict = None, proxy: bool = False):
    proxy_address = random.choice(list(config.PROXIES.values()))

    if proxy is True and proxy in config.PROXIES:
        proxy_address = config.PROXIES[proxy]

    async with ClientSession(timeout=ClientTimeout(10)) as session:
        async with session.request(method, url, headers=headers, cookies=cookies, json=data, proxy=config.PROXY_TEMPLATE.format(proxy_address)) as response:
            length = response.content_length

            if length is not None and length > 10 * 1024 * 1024:
                return {
                    "status": -1,
                    "text": "Content too large",
                    "json": {}
                }

            content = await response.read()

            data = {}

            if response.content_type == "application/json":
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    data = {}

            return {
                "status": response.status,
                "text": content.decode(response.get_encoding()),
                "json": data
            }

async def execute_webhook(webhook_id, webhook_token, *, username = None, avatar_url = None, content = None, embed: femcord.Embed = None):
    data = {}

    if username:
        data["username"] = username
    if avatar_url:
        data["avatar_url"] = avatar_url
    if content:
        data["content"] = content
    if embed:
        data["embeds"] = [embed.__dict__]

    await request("POST", femcord.http.HTTP.URL + "/webhooks/" + webhook_id + "/" + webhook_token, data=data)

def void(*args, **kwargs):
    return False

modules = {
    "requests": {
        "builtins": {
            "request": request,
            "get": lambda *args, **kwargs: request("GET", *args, **kwargs),
            "post": lambda *args, **kwargs: request("POST", *args, **kwargs),
            "patch": lambda *args, **kwargs: request("PATCH", *args, **kwargs),
            "put": lambda *args, **kwargs: request("PUT", *args, **kwargs),
            "delete": lambda *args, **kwargs: request("DELETE", *args, **kwargs)
        }
    }
}

builtins = {
    "Embed": femcord.Embed,
    "execute_webhook": execute_webhook,
    "table": table
}

async def get_modules(bot, guild, *, ctx = None, user = None, message_errors = False):
    query = Guilds.filter(guild_id=guild.id)
    db_guild = await query.first()

    database = db_guild.database

    async def db_update(key, value):
        database[key] = value
        await query.update(database=database)
        return value

    async def db_delete(key):
        database.pop(key)
        await query.update(database=database)

    async def lastfm():
        nonlocal user

        user = user or ctx.author
        lastfm = await LastFM.filter(user_id=user.id).first()

        if lastfm is None:
            if message_errors is True:
                if ctx.author is user:
                    await ctx.reply("Nie masz połączonego konta LastFM, użyj `login` aby je połączyć")

                await ctx.reply("Ta osoba nie ma połączonego konta LastFM")

            return {}

        async with Client(LASTFM_API_KEY) as client:
            try:
                tracks = await client.recent_tracks(lastfm.username)
            except exceptions.NotFound:
                await ctx.reply("Takie konto LastFM nie istnieje")
                return {}

            if not tracks.tracks:
                await ctx.reply("Nie ma żadnych utworów w historii")
                return {}

            fs_data = {
                "tracks": [],
                "lastfm_user": {
                    "username": tracks.username,
                    "scrobbles": tracks.scrobbles
                },
                "nowplaying": False
            }

            if len(tracks.tracks) == 3:
                fs_data["nowplaying"] = True

            async def append_track(index: int, track: Track) -> None:
                track_info = await client.track_info(track.artist.name, track.title, lastfm.username)
                artist_info = await client.artist_info(track.artist.name, lastfm.username)

                fs_track = Track(
                    artist = artist_info,
                    image = track.image,
                    album = track.album,
                    title = track.title,
                    url = track.url,
                    duration = track.duration,
                    streamable = track.streamable,
                    listeners = track_info.listeners,
                    playcount = track_info.playcount,
                    scrobbles = track_info.scrobbles or "0",
                    tags = track_info.tags,
                    date = track.date
                )

                fs_data["tracks"].append((index, fs_track))

            for index, track in enumerate(tracks.tracks[:2]):
                bot.loop.create_task(append_track(index, track))

            count = 0

            while len(fs_data["tracks"]) < 2:
                await asyncio.sleep(0.1)

                count += 1

                if count > 100:
                    break

            fs_data["tracks"].sort(key=lambda track: track[0])
            fs_data["tracks"] = [track[1] for track in fs_data["tracks"]]

            return fs_data

    return {
        **modules,
        "database": {
            "builtins": {
                "get_all": lambda: dict(**database),
                "get": lambda key: database.get(key, False),
                "update": db_update,
                "delete": db_delete
            },
            "variables": database
        },
        "lastfm": {
            "variables": (
                {
                    **convert(tracks=(lfm := await lastfm()).get("tracks", [])),
                    "lastfm_user": lfm.get("lastfm_user"),
                    "nowplaying": lfm.get("nowplaying")
                }
                if ctx is not None else
                {

                }
            )
        }
    }