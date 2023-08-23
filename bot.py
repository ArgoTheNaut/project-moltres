# Built from quickstart
# https://discordpy.readthedocs.io/en/stable/quickstart.html
# https://github.com/adafruit/Adafruit_CircuitPython_MCP9808
import os
import discord
import board
import adafruit_mcp9808
import time, threading
import asyncio
import datetime

intents = discord.Intents.default()
intents.message_content = True

THRESHOLD_TOO_HOT = 23
POLLING_INTERVAL_SECONDS = 15

global last_sent_on
last_sent_on = 0

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
    # await set_interval(post_temp, POLLING_INTERVAL_SECONDS)

    while True:
        await asyncio.sleep(POLLING_INTERVAL_SECONDS)
        await post_temp()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


async def post_temp():
    global last_sent_on
    # Loose mutex
    if last_sent_on + POLLING_INTERVAL_SECONDS < time.time():
        return
    else:
        last_sent_on = time.time()

    # Send once past mutex
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
