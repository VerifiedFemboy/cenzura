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

import lib
from lib import commands, types
import ast, subprocess, inspect

class Dev(commands.Cog):
    hidden = True

    def __init__(self, bot):
        self.bot = bot

    def insert_returns(self, body):
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)

        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)

    async def _eval(self, code, env = {}):
        content = "\n".join(f"    {x}" for x in code.splitlines())
        body = f"async def penis():\n{content}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        self.insert_returns(body)

        exec(compile(parsed, filename="dupa", mode="exec"), env)

        return await eval("penis()", env)

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(kod)")
    async def eval(self, ctx, *, code):
        if not ctx.author.id in self.bot.owners:
            return await ctx.reply("nie możesz!!1!")

        result = await self._eval(code, {
            "lib": lib,
            "ctx": ctx,
            "bot": self.bot,
            "src": inspect.getsource
        })

        if isinstance(result, lib.Embed):
            return await ctx.reply(embed=result)

        result = str(result)

        if len(result) < 100:
            return await ctx.reply(result)

        chunks = [result[i:i+1991] for i in range(0, len(result), 1991)]

        await ctx.reply("\x60\x60\x60py\n%s\x60\x60\x60" % chunks[0])

        for chunk in chunks[1:]:
            await ctx.send("\x60\x60\x60py\n%s\x60\x60\x60" % chunk)

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(komenda)", aliases=["src"])
    async def source(self, ctx, *, command):
        if not ctx.author.id in self.bot.owners:
            return await ctx.reply("nie możesz!!1!")

        command = command.split(" ")
        command_object = self.bot.get_command(command[0])

        if len(command) > 1:
            while command_object.type is commands.CommandTypes.GROUP:
                command = command[1:]
                if command:
                    command_object = command_object.get_subcommand(command[0])

        code = inspect.getsource(command_object.callback)
        chunks = [code[i:i+1991] for i in range(0, len(code), 1991)]

        await ctx.reply("\x60\x60\x60py\n%s\x60\x60\x60" % chunks[0])

        for chunk in chunks[1:]:
            await ctx.send("\x60\x60\x60py\n%s\x60\x60\x60" % chunk)

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(komenda)")
    async def shell(self, ctx, *, command):
        if not ctx.author.id in self.bot.owners:
            return await ctx.reply("nie możesz!!1!")

        output, error = subprocess.Popen(command, shell=True, executable="/usr/bin/fish", stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        await ctx.send(f"```root in seks via 🐍 v3.10.4\n❯ {command}\n{output.decode() if not error else error.decode()}```")

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(extenszyny)")
    async def load(self, ctx, extensions):
        if not ctx.author.id in self.bot.owners:
            return await ctx.reply("nie możesz!!1!")

        loaded = []

        for extension in extensions.split():
            self.bot.load_extension(extension)

            loaded.append(extension)

        await ctx.reply("\n".join("\N{WHITE HEAVY CHECK MARK} `%s`" % extension_name for extension_name in loaded))

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(extenszyny)")
    async def reload(self, ctx, extensions):
        if not ctx.author.id in self.bot.owners:
            return await ctx.reply("nie możesz!!1!")

        reloaded = []

        for extension in extensions.split():
            self.bot.unload_extension(extension)
            self.bot.load_extension(extension)

            reloaded.append(extension)

        await ctx.reply("\n".join("\N{WHITE HEAVY CHECK MARK} `%s`" % extension_name for extension_name in reloaded))

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(extenszyny)")
    async def unload(self, ctx, extensions):
        if not ctx.author.id in self.bot.owners:
            return await ctx.reply("nie możesz!!1!")

        unloaded = []

        for extension in extensions.split():
            self.bot.unload_extension(extension)

            unloaded.append(extension)

        await ctx.reply("\n".join("\N{WHITE HEAVY CHECK MARK} `%s`" % extension_name for extension_name in unloaded))

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(użytkownik) (komenda) [argumenty]")
    async def su(self, ctx, member: types.Member, command, *, args = None):
        if not ctx.author.id in self.bot.owners:
            return await ctx.reply("nie możesz!!1!")

        message = types.Message(**ctx.message.__dict__)
        message.author = member.user
        message.member = member
        message.content = ctx.guild.prefix + command + " " + (args if args is not None else "")

        await self.bot.gateway.dispatch("message_create", message)

def setup(bot):
    bot.load_cog(Dev(bot))