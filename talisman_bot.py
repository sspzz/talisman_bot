from discord.ext import commands
import discord
import logging
import logging.config
import json
import asyncio
import random
import leaderboard


# Utilities related to Discord
class DiscordUtils:
	@staticmethod
	async def embed(ctx, title, description, thumbnail=None, image=None, url=None, color=None):
		color = color if color is not None else 0x9B59B6
		embed = discord.Embed(title=title, description=description, color=color)
		if thumbnail is not None:
			embed.set_thumbnail(url=thumbnail)
		if image is not None:
			embed.set_image(url=image)
		if url is not None:
			embed.url = url
		await ctx.send(embed=embed)

	@staticmethod
	async def embed_fields(ctx, title, description, fields, inline=True, thumbnail=None, color=None):
		color = color if color is not None else 0x9B59B6
		embed = discord.Embed(title=title, description=description, color=color)
		if thumbnail is not None:
			embed.set_thumbnail(url=thumbnail)
		for field in fields:
			embed.add_field(name=field[0], value=field[1], inline=inline)			
		await ctx.send(embed=embed)


#
# Setup
#
bot = commands.Bot(command_prefix="!")

logging.basicConfig(filename='talisman_bot.log',
                    filemode='a',
                    format='[%(asctime)s] %(name)s - %(message)s',
                    datefmt='%d-%m-%Y @ %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger('talisman_bot')

bot.comp_running = False
djinn_emoji = '<:Djinn:901926932747268166>'
default_rites = 5


def get_wiz_url(wiz_id):
	return "https://opensea.io/assets/0x521f9c7505005cfa19a8e5786a9c3c9c9f5e6f42/{}".format(wiz_id)

def get_admins():
	with open('admins.txt', 'r') as file:
		return [int(line.rstrip()) for line in file.readlines()]
	return []

def is_admin():
	def predicate(ctx):
		return ctx.message.author.id in get_admins()
	return commands.check(predicate)


@bot.command(name="talisman", aliases=["tal"])
async def show_info(ctx):
	logger.info("WTF")
	title = "Talisman"
	description = """There is a Talisman few have heard of and even fewer have seen. It has been at the center of adventure, at the purpose of war, and at the heart of faith. It has crossed the Seventh Realm and delved into the Quantum Shadow.

In spells of seldom offerings, it will bestow {} Rites across the lands of the Forgotten Runes to anyone who is there to claim them, worthy or not—for it is ruled only by chaos. These {} Rites are pieces of a ceremony—the credentials of a summoning—and give dominion over the Talisman’s powers; with the correct amount, you may be able to unlock its great and terrible force.

Be vigilant and be quick in acquiring {} Rites, for many seek to use the magic of the Talisman!""".format(djinn_emoji, djinn_emoji, djinn_emoji)
	await DiscordUtils.embed(ctx, title, description)


@bot.command(name="leaderboard", aliases=["board"])
async def show_leaderboard(ctx):
	lb = leaderboard.rankings(ctx.guild.id)

	if len(lb) < 1:
		await ctx.send("No {} Rites have been bestowed.".format(djinn_emoji))
		return

	async def get_users(users):
		res = {}
		for user in users:
			u = await bot.fetch_user(user[0])
			res[user[0]] = u
		return res
	usernames = await get_users(lb)

	lines = list(map(lambda e: "**{}.** {} - {} {} Rites".format(lb.index(e)+1, usernames[e[0]], djinn_emoji, e[1]), lb))
	await DiscordUtils.embed(ctx=ctx, title="Leaderboard", description="\n".join(lines))


@bot.command(name="rank", aliases=["bal", "balance"])
async def show_rank(ctx):
	rankings = leaderboard.rankings(ctx.guild.id)
	user = [rank for rank in rankings if rank[0] == ctx.message.author.id][0]
	if user is not None:
		user_avatar = ctx.message.author.avatar_url
		user_name = await bot.fetch_user(user[0])
		user_score = user[1]
		user_rank = rankings.index(user)+1
		fields = [("Balance", "{} {} Rites".format(djinn_emoji, user_score))]
		await DiscordUtils.embed_fields(ctx=ctx,
										title=user_name, 
										description="Leaderboard rank #{}".format(user_rank), 
										fields=fields, 
										thumbnail=user_avatar)


@bot.command(name="bestow")
@is_admin()
async def bestow(ctx, num, mentions):
	if num is None:
		await ctx.send("Please specify the number of {} Rites to bestow.".format(djinn_emoji))
		return
	else:
		try:
			num = int(num)
		except:
			await ctx.send("You must specify a correct number!")
			return

	if len(ctx.message.mentions) < 1:
		await ctx.send("Please specify to whom I should bestow {} Rites.".format(djinn_emoji))
		return

	for user in ctx.message.mentions:
		leaderboard.grant_points(user.id, num, ctx.guild.id)
		await ctx.send("{} has been bestowed {} {} Rites".format(user, djinn_emoji, num))


@bot.command(name="offering", aliases=["offer"])
@is_admin()
async def offering(ctx, num=None):
	if bot.comp_running:
		await ctx.send("A Rite is already being performed.")
		return
	
	if num is None:
		num = default_rites
	else:
		try:
			num = int(num)
		except:
			await ctx.send("You must specify a correct number!")
			return

	bot.comp_running = True

	try:
		# Send a message, first to react with the correct emoji wins
		botmsg = await ctx.send("Hurry now, first {} is bestowed {} Rites.".format(djinn_emoji, num))
		# await botmsg.add_reaction(djinn_emoji)

		def verify_emoji(reaction, user):
			return str(reaction.emoji) == djinn_emoji

		reaction, user = await bot.wait_for('reaction_add', timeout=15.0, check=verify_emoji)
		bot.comp_running = False
		leaderboard.grant_points(user.id, num, ctx.guild.id)
		await ctx.send('Congrats {}, you have been bestowed {} {} Rites.'.format(user.name, djinn_emoji, num))
		
	except asyncio.TimeoutError:
		bot.comp_running = False
		await ctx.send('Too slow.')


@bot.command(name="riddle")
@is_admin()
async def riddle(ctx, num=None):
	try:
		riddles = json.load(open("riddles.json", 'r'))
		riddle, answer = random.choice(list(riddles.items()))
	except:
		return


	if bot.comp_running:
		await ctx.send("A Rite is already being performed.")
		return
	
	if num is None:
		num = default_rites
	else:
		try:
			num = int(num)
		except:
			await ctx.send("You must specify a correct number!")
			return

	bot.comp_running = True

	try:
		# Send a message, first to react with the correct emoji wins
		botmsg = await ctx.send("Riddle me this: \"{}\" First right answer is bestowed {} {} Rites.".format(riddle, djinn_emoji, num))
		# await botmsg.add_reaction(djinn_emoji)

		def verify_message(message):
			return message.content.lower() == answer.lower()

		msg = await bot.wait_for('message', timeout=15.0, check=verify_message)
		user = msg.author
		bot.comp_running = False
		leaderboard.grant_points(user.id, num, ctx.guild.id)
		await ctx.send('Congrats {}, you have been bestowed {} {} Rites.'.format(user.name, djinn_emoji, num))
		
	except asyncio.TimeoutError:
		bot.comp_running = False
		await ctx.send('Too slow.')


#
# Run bot
#
try:
	file = open('creds.json', 'r')
	access_token = json.load(file)['access_token']	
	bot.run(access_token)
except:
	print("Missing or faulty creds.json")

# TODO: random awake and start raffle?
