# Built from quickstart
# https://discordpy.readthedocs.io/en/stable/quickstart.html
# https://github.com/adafruit/Adafruit_CircuitPython_MCP9808
import os
import discord
import board
import adafruit_mcp9808

intents = discord.Intents.default()
intents.message_content = True

CHANNELS = {"stdout": 1134634193998065745, "stderr": 1134634212390084628}

client = discord.Client(intents=intents)


async def send_status_update_normal(info: str):
    channel = client.get_channel(CHANNELS["stdout"])
    print("Retrieved channel:", channel)
    await channel.send(info)


async def send_warning(info: str):
    channel = client.get_channel(CHANNELS["stderr"])
    print("Retrieved channel:", channel)
    await channel.send(info)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await send_status_update_normal("Standard Message")
    await send_warning("Standard warning test")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


with open("token.txt", "r") as auth_token:
    client.run(auth_token.read())

with board.I2C() as i2c:
    t = adafruit_mcp9808.MCP9808(i2c)
    print(t.temperature)
