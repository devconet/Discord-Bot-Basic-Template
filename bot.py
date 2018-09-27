import discord
from discord.ext import commands
from utils import checks, output, parsing
import os

config = parsing.parse_json('config.json')
skip_cogs=config['skip_cogs']

bot = commands.Bot(command_prefix=config['prefix'], description=config["description"])

try:
    os.remove("log.txt")
except FileNotFoundError:
    pass

startup_extensions = os.listdir("./cogs")
if "__pycache__" in startup_extensions:
    startup_extensions.remove("__pycache__")
startup_extensions = [ext.replace('.py', '') for ext in startup_extensions]
loaded_extensions = []
startup_extensions=[x for x in startup_extensions if x not in skip_cogs]

@bot.event
async def on_ready():
    output.info("Loading {} extension(s)...".format(len(startup_extensions)))

    for extension in startup_extensions:
        try:
            bot.load_extension("cogs.{}".format(extension.replace(".py", "")))
            loaded_extensions.append(extension)

        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('Failed to load extension {}\n\t->{}'.format(extension, exc))
    output.success('Successfully loaded the following extension(s): {}'.format(', '.join(loaded_extensions)))
    output.info('You can now invite the bot to a server using the following link: https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(bot.user.id))

@bot.event
async def on_message(message):
    # disregard messages sent by our own bot
    if message.author.id == bot.user.id:
        return     

    await bot.process_commands(message)


@bot.command(pass_context=True, hidden=True)
@commands.check(checks.is_owner)
async def shutdown(ctx):
    """Shut down the bot"""
    author = str(ctx.message.author)

    try:
        await bot.say("Shutting down...")
        await bot.logout()
        bot.loop.stop()
        output.info('{} has shut down the bot...'.format(author))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        output.error('{} has attempted to shut down the bot, but the following '
                     'exception occurred;\n\t->{}'.format(author, exc))


#region Server Events
@bot.event
async def on_server_join(server):
    output.info("Added to {0}".format(server.name))

@bot.event
async def on_server_leave(server):
    output.info("Removed from {0}".format(server.name))
#endregion


#region Command Error
@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.CommandInvokeError):
        output.error("Exception in command '{}', {}".format(ctx.command.qualified_name, error.original))
        oneliner = "Error in command '{}' - {}: {}\nIf this issue persists, Please report it in the support server.".format(
            ctx.command.qualified_name, type(error.original).__name__, str(error.original))
        await ctx.bot.send_message(channel, oneliner)

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            em = discord.Embed(title="Missing args :x:",
                               description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.red())
            await bot.send_message(ctx.message.channel, embed=em)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            em = discord.Embed(title="Missing args :x:",
                               description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.red())
            await bot.send_message(ctx.message.channel, embed=em)
#endregion

@bot.command()
async def add(num1 : int, num2 : int):
    '''Add two numbers'''
    await bot.say(num1 + num2)

bot.run(config["discord"]["token"])
bot.loop.close()
