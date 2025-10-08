import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import dotenv
import json
from wordlefunc import *
import atexit

# Load environment variables from .env file
dotenv.load_dotenv()

def exit_handler():
    global users
    logging.info("Shutting down...")
    with open("users.json", "w") as f:
        json.dump([user.to_dict() for user in users.values()], f)
    logging.shutdown()

atexit.register(exit_handler)

#Time Cog to handle daily getting new word
class TimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("TimeCog initialized.")

    def cog_unload(self):
        self.check_daily.cancel()

    async def cog_load(self):
        self.check_daily.start()
        logger.info("Daily check started.")

    def seconds_until_midnight(self):
        now = datetime.datetime.now()
        midnight = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return (midnight - now).total_seconds()


    @tasks.loop(hours=24)
    async def check_daily(self):
        await asyncio.sleep(self.seconds_until_midnight())
        logger.info(f"New word of the day: {getWordOfTheDay()}")
        logger.info("Resetting boards for all users.")
        global users
        for user in users.values():
            user.check_date()
        with open("users.json", "w") as f:
            json.dump([user.to_dict() for user in users.values()], f)
        logger.info("All boards reset.")


class YappleUser:
    def __init__(self, user_id):
        self.user_id = user_id
        self.board = Board()
        self.stats = {
            "games_played": 0,
            "current_streak": 0,
            "max_streak": 0,
            "guess_distribution": [0, 0, 0, 0, 0, 0, 0]
        }

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "board": self.board.to_dict(),
            "stats": self.stats
        }

    def from_dict(data):
        user = YappleUser(data["user_id"])
        user.board = Board.from_dict(data["board"])
        user.stats = data["stats"]
        return user

    def check_date(self):
        if self.board.date != datetime.date.today().isoformat():
            if not self.board.is_complete:
                self.stats["current_streak"] = 0
                self.stats["games_played"] += 1
                self.stats["guess_distribution"][6] += 1
            if self.board.date != (datetime.date.today() - datetime.timedelta(days=1)).isoformat():
                self.stats["current_streak"] = 0
            self.board = Board()
        return

    def display_stats(self):
        stats = self.stats
        fire = "" if stats["current_streak"] < 3 else "🔥" * (1 if stats["current_streak"] < 6 else 3)
        stats_message = (f"User: <@{self.user_id}>\n"
                         f"Games Played: {stats['games_played']}\n"
                         f"Current Streak: {stats['current_streak']} " + fire +"\n"
                         f"Max Streak: {stats['max_streak']}\n"
                         "Guess Distribution:\n")
        for i, count in enumerate(stats['guess_distribution']):
            if i == 6:
                stats_message += f"X/6: {count}\n"
                continue
            stats_message += f"{i + 1}/6: {count}\n"
        return stats_message


class YappleClient(commands.Bot):
    def __init__(self, **options):
        super().__init__(**options)
        # Get users
        global users
        users = {}
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                if os.stat("users.json").st_size == 0:
                    data = []
                else:
                    data = json.load(f)
                for user in data:
                    users[user["user_id"]] = YappleUser.from_dict(user)
            logger.info(f"Loaded {len(users)} users from file.")
        else:
            logger.info("No users file found, starting fresh.")
        wordOfTheDay = getWordOfTheDay()
        logger.info(f"Word of the day: {wordOfTheDay}")

    async def setup_hook(self):
        await self.add_cog(TimeCog(self))
        self.tree.add_command(yapple_command)
        self.tree.add_command(guess_command)
        self.tree.add_command(stats_command)
        self.tree.add_command(help_command)
        self.tree.add_command(board_command)
        self.tree.add_command(used_command)
        test_guild = discord.Object(id=1034538537699266601)
        await self.tree.sync(guild=test_guild)  # Sync commands globally
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        logger.info(f'Logged in as {self.user}')


@app_commands.command(name="yapple", description="Get information about the Yapple bot.")
async def yapple_command(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Yapple is a Wordle bot. Use the command `/guess <guess>` in this dm to play. You can also use the command `/help` to get help.")
    else:
        # Get user ids of guild members
        member_ids = [str(member.id) for member in interaction.guild.members if not member.bot]
        # Construct message with who has completed today's wordle and their attempts
        message = "Today's Yapple attempts:\n"
        for user_id in member_ids:
            if user_id in users:
                user = users[user_id]
                user.check_date()
                if user.board.is_complete:
                    message += f"<@{user_id}>: {user.board.current_row}/6\n"
        if message == "Today's Yapple attempts:\n":
            message += "No one has completed today's Yapple yet."
        await interaction.response.send_message(message)

@app_commands.command(name="help", description="Get help with Yapple commands.")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Commands:\n`/yapple` - Get information about the bot.\n"
        "`/guess <guess>` - Make a guess in your current game.\n`"
        "'/stats <user>` - View game statistics.\n"
        "`/board` - Display your current board.\n"
        "`/used` - Display your used letters.\n"
        "You can also use the command `/yapple` in any server channel to other people's attempts today")

@app_commands.command(name="guess", description="Make a guess in your current game.")
@app_commands.describe(guess="Your 5-letter guess")
async def guess_command(interaction: discord.Interaction, guess: str):
    user_id = str(interaction.user.id)
    if user_id not in users:
        users[user_id] = YappleUser(user_id)
    user = users[user_id]
    user.check_date()
    if user.board.is_complete:
        await interaction.response.send_message("You have already completed today's Wordle. Come back tomorrow!")
        return
    result = user.board.userGuess(guess)
    if user.board.is_complete:
        user.stats["games_played"] += 1
        result += f"\nThe word was: {user.board.solution}"
        await interaction.response.send_message(result, ephemeral=True)
        if user.board.current_row < 6:
            user.stats["current_streak"] += 1
            user.stats["max_streak"] = max(user.stats["max_streak"], user.stats["current_streak"])
            user.stats["guess_distribution"][user.board.current_row - 1] += 1
        else:
            user.stats["current_streak"] = 0
            user.stats["guess_distribution"][6] += 1
    else:
        await interaction.response.send_message(result)
    # Save users' boards to file
    with open("users.json", "w") as f:
        json.dump([user.to_dict() for user in users.values()], f)

@app_commands.command(name="stats", description="View game statistics.")
@app_commands.describe(user="The user to view statistics for")
async def stats_command(interaction: discord.Interaction, user: discord.User):
    user_id = str(user.id)
    if user_id not in users:
        users[user_id] = YappleUser(user_id)
    user = users[user_id]
    user.check_date()
    stats_message = user.display_stats()
    await interaction.response.send_message(stats_message)

@app_commands.command(name="board", description="Display your current board.")
async def board_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in users:
        users[user_id] = YappleUser(user_id)
    user = users[user_id]
    user.check_date()
    board_display = user.board.display()
    if board_display is None:
        await interaction.response.send_message("No current game. Start a new game by making a guess with `/guess <word>`.", ephemeral=True)
        return
    await interaction.response.send_message(board_display)

@app_commands.command(name="used", description="Display your used letters.")
async def used_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in users:
        users[user_id] = YappleUser(user_id)
    user = users[user_id]
    user.check_date()
    used_letters = ', '.join(sorted(user.board.used_letters))
    await interaction.response.send_message(f"Used letters: {used_letters}", ephemeral=True)

yapple = YappleClient(command_prefix="/", intents=discord.Intents.all())
users = {}
yapple.run(os.getenv("SECRET"))