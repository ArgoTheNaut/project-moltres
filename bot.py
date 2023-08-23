# Built from quickstart
# https://discordpy.readthedocs.io/en/stable/quickstart.html
# https://github.com/adafruit/Adafruit_CircuitPython_MCP9808
import os
import discord
import board
import adafruit_mcp9808
import time, threading
import datetime
from discord.ext import tasks, commands

intents = discord.Intents.default()
intents.message_content = True

THRESHOLD_TOO_HOT = 23
POLLING_INTERVAL_SECONDS = 5 * 60

CHANNELS = {"stdout": 1134634193998065745, "stderr": 1134634212390084628}

client = discord.Client(intents=intents)


# Standard output channel
# This should be safe to mute, but exists for logging and debugging purposes
async def stdout(info: str):
    channel = client.get_channel(CHANNELS["stdout"])
    print("Retrieved channel:", channel)
    await channel.send(info)


# Standard error channel
# This should have notifications set to occur regularly.
async def stderr(info: str):
    channel = client.get_channel(CHANNELS["stderr"])
    print("Retrieved channel:", channel)
    await channel.send(info)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    Thermometer()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


# https://discordpy.readthedocs.io/en/latest/ext/tasks/
# https://stackoverflow.com/a/64167767
class Thermometer(commands.Cog):
    def __init__(self):
        self.post_temp.start()

    @tasks.loop(seconds=POLLING_INTERVAL_SECONDS)
    async def post_temp(self):
        temp = get_temp()
        if temp > THRESHOLD_TOO_HOT:
            await stderr(f"TEMPERATURE IS TOO HOT: {temp} Celcius")
        else:
            await stdout(f"Temperature within normal range. {temp} Celcius")


def get_temp():
    print("Acquiring temperature at", datetime.datetime.now())
    with board.I2C() as i2c:
        t = adafruit_mcp9808.MCP9808(i2c)
        return t.temperature


with open("token.txt", "r") as auth_token:
    client.run(auth_token.read())
