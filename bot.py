# Built from quickstart
# https://discordpy.readthedocs.io/en/stable/quickstart.html
# https://github.com/adafruit/Adafruit_CircuitPython_MCP9808
import os
import discord
import board
import adafruit_mcp9808
import time, threading

intents = discord.Intents.default()
intents.message_content = True

THRESHOLD_TOO_HOT = 23
POLLING_INTERVAL_SECONDS = 5

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

    StartTime = time.time()

    # start action every 0.6s
    inter = setInterval(POLLING_INTERVAL_SECONDS, action)
    print("just after setInterval -> time : {:.1f}s".format(time.time() - StartTime))

    # will stop interval in 50s
    t = threading.Timer(50, inter.cancel)
    t.start()


def action():
    print("Temperature read event!")
    post_temp()


# Class written by: https://stackoverflow.com/users/1619521/doom
# Source: https://stackoverflow.com/a/48709380
class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime = time.time() + self.interval
        while not self.stopEvent.wait(nextTime - time.time()):
            nextTime += self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


async def post_temp():
    temp = get_temp()
    if temp > THRESHOLD_TOO_HOT:
        await stderr(f"TEMPERATURE IS TOO HOT: {temp} Celcius")
    else:
        await stdout(f"Temperature within normal range. {temp} Celcius")


def get_temp():
    print("Acquiring temperature")
    with board.I2C() as i2c:
        t = adafruit_mcp9808.MCP9808(i2c)
        return t.temperature


with open("token.txt", "r") as auth_token:
    client.run(auth_token.read())
