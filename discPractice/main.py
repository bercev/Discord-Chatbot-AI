from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response
import certifi
from collections import defaultdict
from discord.ext import commands
import json
from create_and_change_db import add_to_db

os.environ["SSL_CERT_FILE"] = certifi.where()


# Load our token from somewhere safe
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
banned_words = os.getenv('banned_words')
banned_words = banned_words.split(',')

# Bot Setup
intents: Intents = Intents.default()
intents.message_content = True # NOQA
client: Client = commands.Bot(command_prefix=[">>"], intents=intents)

# deleted message holder
recentlyDeleted = "No messages have been recently deleted"

# Flag to control message processing
processing_messages = True

# Message Functionality
async def send_message(message: Message, user_message: str, deleted: bool=False) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probs)')
        return
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    if message.author == client.user:
        return
    try:
        # this if block checks if a message that has been deleted wants to be viewed
        if '>>snipe' in user_message.lower():
            response: str = recentlyDeleted # new version of deleted only works when '>>Snipe' is mentioned
            # {old version} --> response: str = get_response(user_message, deleted=True)
        elif '>>purge' in user_message.lower(): # purging messages
            num = 2
            try:
                num = int(user_message[user_message.index('e')+1:])
            except Exception as e:
                print(e)

            guild = client.get_guild(message.guild.id)
            channel = guild.get_channel(message.channel.id)

            deleted = await channel.purge(limit=num)
            await channel.send(f'Deleted {len(deleted)} message(s)')
            return
        else:
            response: str = get_response(user_message)
        if not response:
            return
        await message.author.send(response) if is_private else await message.channel.send(response)
        
        ''' if a question is asked to the chatbot, sleep for 5 seconds to ensure the AI model isn't overloaded because of server requests 
        as it is hosted on the Hugging Face Inference API
    
        if '>>' in user_message:
            processing_messages = False
            sleepTime: str = "Not processing any messages for the next 5 seconds..."
            await message.author.send(sleepTime) if is_private else await message.channel.send(sleepTime)
            await asyncio.sleep(5)
            processing_messages = True
            await message.author.send("Im back!") if is_private else await message.channel.send("Im back!")
            '''
    except Exception as e:
        print(e)
        print("line82")


# Handling incoming messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    u_msg = user_message.lower()

    # cleaning up the message 
    for i in banned_words:
        if i in u_msg:
            idx = u_msg.index(i)
            u_msg = u_msg[0:idx+1] + "#"*(len(i)-1) + u_msg[len(i) + idx:]

    # adding message to db if it is not a command
    if ">>" not in u_msg:
        add_to_db(u_msg, {"source": message.author.mention}, message.id)


    print(f'[{channel}] {username}: {u_msg}')
    await send_message(message, user_message)


# Detects deleted messages
@client.event
async def on_message_delete(message: Message) -> None:
    if message.author == client.user:
        return

    user_message: str = message.content
    channel: str = str(message.channel)

    user_message = f'**{message.author.mention} in #{channel} recently deleted:** {user_message}'
    print(user_message)

    # await send_message(message, user_message, deleted=True) <-- Old version; always shows deleted message
    global recentlyDeleted 
    recentlyDeleted = user_message


# Handling the startup for our bot
@client.event
async def on_read(message: Message) ->None:
    print(f'{client.user} is now running!')
    await send_message(message, "Bot is now live!")


# Status update of the bot when it first goes live
@client.event
async def on_ready():
    print("BOT IS NOW LIVE!")
    # Ensure the bot is ready before accessing the guild
    guildList = []
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.name == 'general' and ("Text Channels" == str(channel.category)):
                guildList.append((guild.id,channel.id))


    for group in guildList:
        guild = client.get_guild(group[0])
        channel = guild.get_channel(group[1])
        await channel.send("```\n**BOT IS NOW LIVE!**\nCommands:\nRoll dice === generates a random number between 1-6" + 
                    "\n>>[question]? === asks a question to Llama AI. Include [###] in query to get a ### character length response"+
                    "\n>>query [question]? === answers a question based off of chat history\n```")


# Main entry point
def main() -> None:
    client.run(token=TOKEN)

#lambda
def lambda_handler(event, context):
    print(event)
    client.run(TOKEN)

if __name__ == '__main__':
    main()

