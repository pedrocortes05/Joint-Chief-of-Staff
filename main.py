import asyncio
import datetime
import json
import math
import re
import traceback
from datetime import timedelta

import discord
from discord.ext import commands, tasks
from discord.utils import get
from DiscordUtils import Pagination
from pytz import timezone

import tokens

current_token = tokens.TOKEN
DB = tokens.DB

async def save_prefix(guild_id, prefix):
	extension = f"-prefixes"
	text_channel = (client.user.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	prev_prefix = [prefix async for prefix in channel.history() if prefix.content.split(prefix_separator)[0] == str(guild_id)]
	if bool(prev_prefix): await prev_prefix[0].delete()
	await channel.send(str(guild_id) + prefix_separator + prefix)

	#reload prefixes globally
	await get_prefixes()

async def get_prefixes():
	extension = f"-prefixes"
	text_channel = (client.user.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	global prefixes
	prefixes = {message.content.split(prefix_separator)[0]:message.content.split(prefix_separator)[1] async for message in channel.history()}

def get_prefix(client, ctx):
	try:
		prefix = prefixes[str(ctx.guild.id)]
	except:
		prefix = '!'

	return prefix

intents = discord.Intents().all()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix=get_prefix, intents=intents, case_insensitive=True)
client.remove_command("help")
msg_separator = "<=message:author=>"
prefix_separator = "<=guild:prefix=>"
defcon_separator = "<=level:category=>"
task_separator = "<=:=>"

async def reload_guild_dB(text_channel):
	dB_category = get(dB_guild.categories, name="Database")
	if text_channel not in [channel.name for channel in dB_category.channels]:
		await dB_guild.create_text_channel(text_channel, category=dB_category)

async def send_msg(message):
	channel = client.get_channel(847741380402348032) #TODO
	await channel.send(message)

async def save_message(guild, category, message, reactor):
	extension = f"-{category}-msgs"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	await channel.send(message + msg_separator + reactor.mention)

async def delete_message(guild, category, index):
	extension = f"-{category}-msgs"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	message = [message async for message in channel.history()][index]
	await message.delete()

async def get_saved_messages(guild, category):
	extension = f"-{category}-msgs"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	messages = [message.content.split(msg_separator) async for message in channel.history()]
	return messages

async def save_defcon(guild, category, level):
	extension = f"-defcon"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)

	prev_level = [message async for message in channel.history() if message.content.split(defcon_separator)[1] == category]
	if bool(prev_level): await prev_level[0].delete()

	await channel.send(level + defcon_separator + category)

async def get_defcon(guild, category):
	extension = f"-defcon"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	level = [message.content.split(defcon_separator)[0] async for message in channel.history() if message.content.split(defcon_separator)[1] == category][0]
	return level

async def save_timezone(guild, timezone):
	extension = f"-timezone"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	prev_timezone = [message async for message in channel.history()]
	if bool(prev_timezone):
		prev_timezone = prev_timezone[0]
		await prev_timezone.delete()

	await channel.send(timezone)

async def get_timezone(guild):
	extension = f"-timezone"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	messages = [message.content async for message in channel.history()]
	if bool(messages):
		timezone = messages[0]
	else:
		timezone = messages

	return timezone

def get_timezones():
	timezones = ""
	for delta in range(-11, 13):
		timezones += f"{delta + 12}. " + f"(GMT{f'+{delta}' if delta >= 0 else delta}) `" + datetime.datetime.now(datetime.timezone(timedelta(hours=delta))).strftime("%H:%M") + "`\n"
	return timezones[:-1]

async def save_task(guild, channel_id, message, interval, start):
	extension = f"-tasks"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	await channel.send(message + task_separator + str(channel_id) + task_separator + str(interval) + task_separator + str(start))

async def delete_task(guild, index):
	extension = f"-tasks"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	task = [message async for message in channel.history()][index]
	await task.delete()

async def get_tasks(guild):
	extension = f"-tasks"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	tasks = [message.content.split(task_separator) async for message in channel.history()]
	return tasks

async def save_ticket(guild, num):
	extension = f"-tickets"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	await channel.send(str(num))

async def get_ticket(guild):
	extension = f"-tickets"
	text_channel = (guild.name + extension).replace(' ', '-').lower()
	await reload_guild_dB(text_channel)

	channel = get(dB_guild.channels, name=text_channel)
	num = [num.content async for num in channel.history()]
	if not bool(num): num = ['0']
	return num[0]


@client.event
async def on_ready():
	loop_checker.start()
	await client.change_presence(status=discord.Status.online, activity=discord.Game("Testing"))
	print(f"Logged in as {client.user}")
	global dB_guild
	dB_guild = client.get_guild(DB)
	await get_prefixes()

@client.group(invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def help(ctx):
	embed = discord.Embed(title="Commands", color=ctx.me.color)
	embed.set_author(name=client.user.name, icon_url=client.user.avatar)
	prefix = get_prefix(client, ctx)

	player_commands = f"""**{prefix}SMessage** or **{prefix}smsg**: - Set a re-ocurring message
							**{prefix}LSchedule** or **{prefix}lsmsg**: - View scheduled messages
							**{prefix}DSchedule** or **{prefix}dsmsg**: - View scheduled messages
							**{prefix}Messages** or **{prefix}msgs**: - View saved messages
							**{prefix}DMessages** or **{prefix}dmsg**: - Delete a saved message
							**{prefix}Say** or **{prefix}s**: - Speak as the bot
							**{prefix}Defcon** or **{prefix}def**: - Set a DEFCON level
							**{prefix}Channel** or **{prefix}ch**: - Create a channel with staff and someone
							**{prefix}ChangePrefix**: - Change the bots prefix"""

	embed.add_field(name="\u200b", value=player_commands, inline=False)
	await ctx.send(embed=embed)

@client.command(aliases=["smsg"])
@commands.has_permissions(administrator=True)
async def SMessage(ctx):
	embed = discord.Embed(title="Type the message", color=discord.Colour.blue())
	embed.set_footer(text='Type "cancel" to stop')
	await ctx.send(embed=embed)
	try:
		reply_msg = await client.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id, timeout=60)
		if reply_msg.content.lower() == "cancel":
			embed = discord.Embed(title="Cancelled", color=discord.Colour.red())
			await ctx.send(embed=embed)
			return

		message = reply_msg.content
	except asyncio.TimeoutError:
		await ctx.send("Time's up")
		return

	embed = discord.Embed(title="Which channel should this message be sent to?", color=discord.Colour.blue())
	embed.add_field(name="Example:", value=ctx.channel.mention)
	embed.set_footer(text='Type "cancel" to stop')
	await ctx.send(embed=embed)

	while True:
		try:
			reply_channel = await client.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id, timeout=60)
			if reply_channel.content.lower() == "cancel":
				embed = discord.Embed(title="Cancelled", color=discord.Colour.red())
				await ctx.send(embed=embed)
				return

			channel = False
			for channel_x in ctx.guild.channels:
				if reply_channel.content == str(channel_x.mention):
					channel = channel_x
					break
			if bool(channel):
				break
			else:
				await ctx.send(f"**{reply_channel.content}** is not a valid channel, please try again")
		except asyncio.TimeoutError:
			await ctx.send("Time's up")
			return

	#check if have timezone
	if not bool(await get_timezone(ctx.guild)):
		embed = discord.Embed(title="You do not have a timezone set.", color=discord.Colour.blue())
		embed.add_field(name="Enter the number corresponding to your timezone", value=get_timezones())
		embed.set_footer(text='Type "cancel" to stop')
		await ctx.send(embed=embed)

		while True:
			try:
				reply_tmz = await client.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id, timeout=60)
				if reply_tmz.content == "cancel":
					return

				try:
					tmz_index = int(reply_tmz.content) - 1

					if tmz_index < 0 and tmz_index > 23:
						await ctx.send(f"**{reply_tmz.content}** is not a valid number, please try again")
					else:
						break
				except ValueError:
					await ctx.send(f"**{reply_tmz.content}** is not recognized as a valid number, please try again")
			except asyncio.TimeoutError:
				await ctx.send("Time's up")
				return
		
		await save_timezone(ctx.guild, tmz_index)

		embed = discord.Embed(title="Your timezone has been set!", color=discord.Colour.green())
		await ctx.send(embed=embed)
	
	#set how often
	embed = discord.Embed(title="How often do you want to repeat this message", color=discord.Colour.blue())
	embed.add_field(name="\u200b", value="example: 8h 30m\nexample: 1d")
	embed.set_footer(text='Type "cancel" to stop')
	await ctx.send(embed=embed)

	while True:
		try:
			reply = await client.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id, timeout=60)
			reply = reply.content
			if reply.lower() == "cancel":
				embed = discord.Embed(title="Cancelled", color=discord.Colour.red())
				await ctx.send(embed=embed)
				return
			try:
				if 'd' in reply:
					interval_days = int(reply[reply.index('d') - 1])
					delta = timedelta(days=interval_days)
					break
				elif 'h' in reply and not 'm' in reply:
					interval_hours = int(reply[reply.index('h') - 1])
					delta = timedelta(hours=interval_hours)
					break
				elif 'h' in reply and 'm' in reply:
					interval_hours = int(reply[reply.index('h') - 1])
					interval_minutes = int(reply[reply.index('m') - 1])
					delta = timedelta(hours=interval_hours, minutes=interval_minutes)
					break
				elif 'm' in reply:
					interval_minutes = int(reply[reply.index('m') - 1])
					delta = timedelta(minutes=interval_minutes)
					break
				else:
					await ctx.send(f"**{reply}**: Invalid interval, please try again")
			except ValueError:
				await ctx.send(f"**{reply}**: Invalid interval, please try again")
			
		except asyncio.TimeoutError:
			await ctx.send("Time's up")
			return
	
	seconds = delta.total_seconds()
	
	#set when to send the message
	embed = discord.Embed(title="When do you want to start the message?", color=discord.Colour.blue())
	embed.add_field(name="\u200b", value="format MM/DD hh:mm\nexample: 11/15 18:05")
	embed.set_footer(text='Type "cancel" to stop')
	await ctx.send(embed=embed)

	#check if response good
	pattern_day = re.compile("^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])$")
	pattern_hour = re.compile("^(((([0-1][0-9])|(2[0-3])):?[0-5][0-9]+$))")

	while True:
		try:
			reply = await client.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id, timeout=60)
			reply = reply.content
			if reply.lower() == "cancel":
				embed = discord.Embed(title="Cancelled", color=discord.Colour.red())
				await ctx.send(embed=embed)
				return

			reply_day, reply_hour = reply.split(' ')
			if not pattern_day.match(reply_day) or not pattern_hour.match(reply_hour):
				await ctx.send(f"**{reply}**: Invalid format, please try again")
			else:
				break
		except asyncio.TimeoutError:
			await ctx.send("Time's up")
			return
	
	month, day = reply_day.split('/')
	hour, minute = reply_hour.split(':')

	start = datetime.datetime(year=int(datetime.datetime.now().year), month=int(month), day=int(day), hour=int(hour), minute=int(minute)).isoformat()

	#confirm selection
	embed = discord.Embed(title='Type "confirm" to set', color=discord.Colour.blue())
	embed.add_field(name="Message", value=message, inline=False)
	embed.add_field(name="Channel", value=reply_channel.content, inline=False)
	embed.add_field(name="First Message Time", value=start, inline=False)
	embed.add_field(name="Interval", value=str(delta), inline=False)
	embed.set_footer(text='Type "cancel" to stop')
	await ctx.send(embed=embed)

	try:
		reply = await client.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id, timeout=60)
		reply = reply.content
		if reply.lower() != "confirm":
			embed = discord.Embed(title="Cancelled", color=discord.Colour.red())
			await ctx.send(embed=embed)
			return
	except asyncio.TimeoutError:
		await ctx.send("Time's up")
		return

	await save_task(ctx.guild, channel.id, message, seconds, start)

	embed = discord.Embed(title="Your message has been scheduled!", color=discord.Colour.green())
	await ctx.send(embed=embed)

@tasks.loop(seconds=60)
async def loop_checker():
	for guild in client.guilds:
		for task in await get_tasks(guild):
			message, channel_id, interval, start = task
			delta = timedelta(seconds=int(float(interval)))
			delta_now = timedelta(seconds=int((datetime.datetime.now(datetime.timezone(timedelta(hours=get_timezone(guild)))) - datetime.datetime.fromisoformat(start)).total_seconds()))
			remaining_seconds = int((math.ceil(delta_now/delta)*delta-delta_now).total_seconds())
			if remaining_seconds < 60:
				channel = client.get_channel(int(channel_id))
				await channel.send(message)

@client.event
async def on_member_join(self, member):
	# Admin channel
	channel = client.get_channel(1044791836889321492)
	await channel.send(f"{member} has joined the server")

@client.command(aliases=["ch"])
@commands.has_permissions(administrator=True)
async def Channel(ctx, *args):
	overwrites = {
    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
    ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
	}
	for mention in ctx.message.mentions:
		overwrites[mention] = discord.PermissionOverwrite(read_messages=True)

	category = get(ctx.guild.categories, id=1044791719281049731) #Admin category
	
	num = int(await get_ticket(ctx.guild)) + 1
	await save_ticket(ctx.guild, num)
	await category.create_text_channel(f"private-{num}", overwrites=overwrites)

@client.event
async def on_reaction_add(reaction, user):
	if str(reaction) == "✅" or str(reaction) == "💾":
		await save_message(reaction.message.guild, reaction.message.channel.category, reaction.message.content, user)
		await reaction.message.channel.send(f"**{reaction.message.content}**: has been saved")

@client.command(aliases=["msgs"])
async def Messages(ctx):
	messages = await get_saved_messages(ctx.guild, ctx.channel.category)
	value = [f"{messages.index(msg) + 1}. " + msg[0] + " => " + msg[1] for msg in messages]
	pages = []
	msg_per_page = 10
	last_page = math.ceil(len(messages)/msg_per_page)

	for page in range(0, last_page):
		start = page * msg_per_page
		end = (page + 1) * msg_per_page
		description = '\n'.join(value[start:end])
		embed = discord.Embed(title=f"Saved Messages in {ctx.channel.category} ({page + 1}/{last_page})", description=description, color=discord.Colour.green())
		embed.set_footer(text="message => saved msg by")
		pages.append(embed)

	paginator = Pagination.CustomEmbedPaginator(ctx)
	paginator.add_reaction("⏪", "first")
	paginator.add_reaction("◀️", "back")
	paginator.add_reaction("▶️", "next")
	paginator.add_reaction("⏩", "first")
	await paginator.run(pages)

@client.command(administrator=True, aliases=["dmsg"])
@commands.has_permissions(administrator=True)
async def DMessage(ctx, num):
	try:
		num = int(num)
	except ValueError:
		await ctx.send(f"**{num}** is not recognized as a valid number")

	messages = await get_saved_messages(ctx.guild, ctx.channel.category)
	if num <= 0 or num > len(messages):
		await ctx.send(f"**{num}** is not a valid message")

	await delete_message(ctx.guild, ctx.channel.category, num - 1)
	await ctx.send(f"Message **{num}** has been deleted")

@client.command(aliases=["s"])
@commands.has_permissions(administrator=True)
async def Say(ctx, *, message):
	await ctx.message.delete()
	await ctx.send(message)

@client.command(aliases=["def"])
@commands.has_permissions(administrator=True)
async def Defcon(ctx):
	categories_list = [category for category in ctx.guild.categories if category.name != "Clan Lobby"]
	categories = ""
	temp_num = 0
	for category in categories_list:
		temp_num += 1
		categories += f"{temp_num}. {category}\n"

	embed = discord.Embed(title="", color=discord.Colour.blue())
	embed.add_field(name="Enter the number to choose a category", value=categories)
	embed.set_footer(text='Type "cancel" to stop')
	await ctx.send(embed=embed)

	while True:
		try:
			reply = await client.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id, timeout=60)
			reply = reply.content
			if reply.lower() == "cancel":
				embed = discord.Embed(title="Cancelled", color=discord.Colour.red())
				await ctx.send(embed=embed)
				return

			try:
				index = int(reply) - 1

				if index < 0 and index >= len(categories_list):
					await ctx.send(f"**{reply}** is not a valid number, please try again")
				else:
					category = categories_list[index]
					break
			except ValueError:
				await ctx.send(f"**{reply}** is not recognized as a valid number, please try again")
		except asyncio.TimeoutError:
			await ctx.send("Time's up")
			return

	embed = discord.Embed(title="Enter the DEFCON level", color=discord.Colour.blue())
	embed.set_footer(text='Type "cancel" to stop')
	await ctx.send(embed=embed)

	while True:
		try:
			reply = await client.wait_for("message", check=lambda m:m.author==ctx.author and m.channel.id==ctx.channel.id, timeout=60)
			reply = reply.content
			if reply.lower() == "cancel":
				embed = discord.Embed(title="Cancelled", color=discord.Colour.red())
				await ctx.send(embed=embed)
				return

			try:				
				level = int(reply)
				break
			except ValueError:
				await ctx.send(f"**{reply}** is not a valid number, please try again")
		except asyncio.TimeoutError:
			await ctx.send("Time's up")
			return

	if level == 1:
		color = discord.Colour.light_grey()
		embed = discord.Embed(title=f"DEFCON {level}", description="COCKED PISTOL", color=color)
		embed.add_field(name="Maximum readiness. Immediate response", value="Nuclear war is imminent or has already started")
	elif level == 2:
		color = discord.Colour.red()
		embed = discord.Embed(title=f"DEFCON {level}", description="FAST PACE", color=color)
		embed.add_field(name="Armed forces ready to deploy and engage in less than six hours", value="Next step to nuclear war")
	elif level == 3:
		color = discord.Colour.yellow()
		embed = discord.Embed(title=f"DEFCON {level}", description="ROUND HOUSE", color=color)
		embed.add_field(name="Air Force ready to mobilize in 15 minutes", value="Increase in force readiness above that required for normal readiness")
	elif level == 4:
		color = discord.Colour.green()
		embed = discord.Embed(title=f"DEFCON {level}", description="DOUBLE TAKE", color=color)
		embed.add_field(name="Above normal readiness", value="Increased intelligence watch and strengthened security measures")
	elif level == 5:
		color = discord.Colour.blue()
		embed = discord.Embed(title=f"DEFCON {level}", description="FADE OUT", color=color)
		embed.add_field(name="Normal readiness", value="Lowest state of readiness")
	else:
		await ctx.send(f"**{level}** is not a valid level")
		return

	await save_defcon(ctx.guild, str(ctx.channel.category), str(level))

	for channel in category.channels:
		await channel.send(embed=embed)

@client.command()
@commands.has_permissions(administrator=True)
async def ChangePrefix(ctx, prefix):
	await save_prefix(ctx.guild.id, prefix)
	await ctx.send(f"Prefix changed to **{prefix}**")


@Channel.error
async def ChannelError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f"Syntax: **{get_prefix(client, ctx)}Channel <@user>**")
		await ctx.send("Multiple users can be mentioned")
	else:
		print(traceback.format_exc())
		print(error)

@DMessage.error
async def DMessageError(ctx, error):
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send(f"Syntax: **{get_prefix(client, ctx)}DMessage <Num>**")
	else:
		print(traceback.format_exc())
		print(error)


client.run(current_token)