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

# How often to poll the temperature and report even if it is not too hot
POLLING_INTERVAL_MINUTES = 5

# How often to poll and report if the temperature is too hot
POLLING_INTERVAL_ALERT_MINUTES = 1

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


retry_attempts = 60
success = False
while (not success) and (retry_attempts > 0):
    retry_attempts -= 1
    success = ip_available()
    print("Checking if IP Requests are able to go through", success)
    print("Response time:", get_delta_time())
    if not success:
        time.sleep(1)  # wait 1 more second for network to maybe be up now?

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
        self.check_temp.start()
        self.check_fire.start()

    @tasks.loop(minutes=POLLING_INTERVAL_MINUTES)
    async def check_temp(self):
        await post_temp(report_cold=True)

    @tasks.loop(minutes=POLLING_INTERVAL_ALERT_MINUTES)
    async def check_fire(self):
        await post_temp(report_cold=False)


def get_temp():
    print("Acquiring temperature at", datetime.datetime.now())
    with board.I2C() as i2c:
        t = adafruit_mcp9808.MCP9808(i2c)
        temp = t.temperature
        print("Found temperature:", temp)
        return temp


async def post_temp(report_cold=True):
    temp = get_temp()
    if temp > THRESHOLD_TOO_HOT:
        await stderr(f"TEMPERATURE IS TOO HOT: {temp} Celcius")
        return
    if report_cold:
        await stdout(f"Temperature within normal range. {temp} Celcius")


baseDir = "/".join(__file__.split("/")[:-1])
with open(baseDir + "/token.txt", "r") as auth_token:
    client.run(auth_token.read())
