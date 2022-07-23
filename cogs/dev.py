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
import ast, inspect

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
    @commands.is_owner
    async def eval(self, ctx, *, code):
        result = await self._eval(code, {
            "lib": lib,
            "ctx": ctx,
            "bot": self.bot,
            "src": inspect.getsource
        })

        if isinstance(result, lib.Embed):
            return await ctx.reply(embed=result)

        result = str(result)

        prefix = "```py\n"
        suffix = "```"

        if len(result) < 100:
            prefix = ""
            suffix = ""

        await self.bot.paginator(ctx.reply, ctx, str(result), prefix=prefix, suffix=suffix)

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(komenda)", aliases=["src"])
    @commands.is_owner
    async def source(self, ctx, *, command):
        command = command.split(" ")
        command_object = self.bot.get_command(command[0])

        if len(command) > 1:
            while command_object.type is commands.CommandTypes.GROUP:
                command = command[1:]
                if command:
                    command_object = command_object.get_subcommand(command[0])

        code = inspect.getsource(command_object.callback)

        await self.bot.paginator(ctx.reply, ctx, code, prefix="```py\n", suffix="```")

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(extenszyny)")
    @commands.is_owner
    async def load(self, ctx, extensions):
        loaded = []

        for extension in extensions.split():
            self.bot.load_extension(extension)

            loaded.append(extension)

        await ctx.reply("\n".join("\N{WHITE HEAVY CHECK MARK} `%s`" % extension_name for extension_name in loaded))

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(extenszyny)")
    @commands.is_owner
    async def reload(self, ctx, extensions):
        reloaded = []

        for extension in extensions.split():
            self.bot.unload_extension(extension)
            self.bot.load_extension(extension)

            reloaded.append(extension)

        await ctx.reply("\n".join("\N{WHITE HEAVY CHECK MARK} `%s`" % extension_name for extension_name in reloaded))

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(extenszyny)")
    @commands.is_owner
    async def unload(self, ctx, extensions):
        unloaded = []

        for extension in extensions.split():
            self.bot.unload_extension(extension)

            unloaded.append(extension)

        await ctx.reply("\n".join("\N{WHITE HEAVY CHECK MARK} `%s`" % extension_name for extension_name in unloaded))

    @commands.command(description="cenzura to bot, bot to cenzura", usage="(użytkownik) (komenda) [argumenty]")
    @commands.is_owner
    async def su(self, ctx, member: types.Member, command, *, args = None):
        message = types.Message(**ctx.message.__dict__)
        message.author = member.user
        message.member = member
        message.content = await self.bot.get_prefix(self.bot, ctx.message) + command + " " + (args if args is not None else "")

        await self.bot.gateway.dispatch("message_create", message)

def setup(bot):
    bot.load_cog(Dev(bot))