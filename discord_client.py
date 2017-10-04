import common
import discord
import asyncio
import re

mentions_regex = re.compile('<@!?[0-9]+>')


class DiscordClient(common.CommonClient):
    def __init__(self,internal_client):
        self.internal_client = internal_client


    async def say(self,target,content):
        await self.internal_client.send_message(target,content)

client = discord.Client()

@client.event
async def on_ready():
    print('Ready for launch!')

@client.event
async def on_message(message):
    if message.author.name != "AlisBot":
        common_client = DiscordClient(client)

        content = message.clean_content
        try:
            content = mentions_regex.sub(message.mentions[0].name,content)
        except:
            pass

        await common.match_command(content,message.channel,message.author.name,common_client)

client.run('')
