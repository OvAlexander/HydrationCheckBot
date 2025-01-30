import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import random
import datetime


def read_lines_from_file(filepath):
    """
    Reads a text file and returns a list of strings, where each string
    represents a line from the file.  Handles potential file not found errors.

    Args:
        filepath: The path to the text file.

    Returns:
        A list of strings, where each string is a line from the file.
        Returns an empty list if the file does not exist or if an error occurs.
    """
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()  # Read all lines into a list
            # Important: Remove newline characters from the end of each line
            cleaned_lines = [line.rstrip('\n') for line in lines]
            return cleaned_lines
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []  # Return an empty list if the file doesn't exist
    # Catch other potential errors (e.g., permission issues)
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def append_string_to_file(filepath, string_to_append):
    """Appends a string to the end of a text file.

    Args:
        filepath: The path to the text file.
        string_to_append: The string to append.
    """
    try:
        with open(filepath, 'a') as file:  # 'a' mode for appending
            file.write(string_to_append)
    except Exception as e:
        print(f"An error occurred while appending to the file: {e}")


def generate_random_time_in_seconds():
    """Generates a random time between 20 and 60 minutes, converted to seconds.

    Returns:
        An integer representing the random time in seconds.
    """

    min_minutes = 0
    max_minutes = 10
    min_seconds = min_minutes*60
    max_seconds = max_minutes*60
    random_seconds = random.randint(
        min_seconds, max_seconds)  # Generates random minutes

    return random_seconds


def check_time():
    """Checks if the current time is between 8 AM and 10 PM using just the time component.

    Returns:
        True if the current time is within the specified range, False otherwise.
    """
    now = datetime.datetime.now().time()  # Get the current time only
    start_time = datetime.time(8, 0)  # 8:00 AM
    end_time = datetime.time(22, 0)  # 10:00 PM

    return start_time <= now <= end_time


def seconds_until():
    """Calculates the number of seconds until the next 8:00 AM.

    Returns:
        The number of seconds until the next 8:00 AM.
    """
    now = datetime.datetime.now()
    next_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)

    if now.time() >= datetime.time(8, 0):  # If it's already 8 AM or later today
        # Go to the next day's 8 AM
        next_8am = next_8am + datetime.timedelta(days=1)

    time_difference = next_8am - now
    return int(time_difference.total_seconds())  # Convert to integer seconds


def get_random_line(filepath):
    """Gets a random line from a text file.

    Args:
        filepath: The path to the text file.

    Returns:
        A string representing a random line from the file, or None if the file
        is empty or an error occurs.  Newline characters are removed.
    """
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            if lines:  # Check if the file is not empty
                # Choose a random line and remove newline
                random_line = random.choice(lines).strip()
                return random_line
            else:
                return None  # Return None for empty files
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


load_dotenv()
DIR_PATH = os.getcwd()
TOKEN = os.getenv('TOKEN')
IP = os.getenv("IP")
SERVER_DIR_PATH = os.getenv(r'SERVER_DIR_PATH')
FILE_PATH = os.getenv('FILE_PATH')
CHANNEL_ID = os.getenv('CHANNEL_ID')
NOTI_LIST = os.getenv('NOTI_LIST')
USER_FILE = "./user_list.txt"
MSG_FILE = "./msg_list.txt"
USERS = read_lines_from_file(USER_FILE)


class Client(discord.Client):

    async def update_presence(self):
        custom_activity = discord.CustomActivity(
            name="It do be Hydration Time")
        await discord.Client.change_presence(self=self,
                                             status=discord.Status.online, activity=custom_activity)

    async def setup_hook(self) -> None:
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.hydration_check())

    async def hydration_check(self):
        await self.wait_until_ready()
        while not self.is_closed():
            for ppl in USERS:
                user = await self.fetch_user(int(ppl))
                msg = get_random_line(MSG_FILE)
                if user.dm_channel is not None:
                    print("Sending Check")
                    await user.dm_channel.send(
                        content=msg)
                else:
                    print("New User")
                    await user.create_dm()
                    await user.dm_channel.send(
                        content=msg)
            # task runs between every 20 mins and 60 mins
            if check_time():
                sec = generate_random_time_in_seconds()
                print(f"awaiting {sec}")
                await asyncio.sleep(sec)
            else:
                await asyncio.sleep(seconds_until())

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        await self.update_presence()


def init():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = Client(intents=intents)
    bot.run(TOKEN)


if __name__ == "__main__":
    init()
