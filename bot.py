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
import platform
from urllib import request

intents = discord.Intents.default()
intents.message_content = True

THRESHOLD_TOO_HOT = 23
POLLING_INTERVAL_MINUTES = 1

CHANNELS = {"stdout": 1134634193998065745, "stderr": 1134634212390084628}

start_time = time.time()


def get_delta_time():
    return time.time() - start_time


# Make sure we're online before proceeding
def ip_available(target="http://8.8.8.8"):
    try:
        request.urlopen(target, timeout=10)
        return True
    except request.URLError as err:
        return False


retry_attempts = 5
while retry_attempts > 0:
    retry_attempts -= 1
    print("Checking if IP Requests are able to go through", ip_available())
    print("Response time:", get_delta_time())

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

    # https://stackoverflow.com/a/799799
    await stdout("Moltres is coming online on computer: " + platform.node())

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

    @tasks.loop(minutes=POLLING_INTERVAL_MINUTES)
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
        temp = t.temperature
        print("Found temperature:", temp)
        return temp


baseDir = "/".join(__file__.split("/")[:-1])
with open(baseDir + "/token.txt", "r") as auth_token:
    client.run(auth_token.read())
