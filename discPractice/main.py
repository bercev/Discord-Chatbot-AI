from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response
import certifi
import asyncio
from collections import defaultdict
from discord.ext import commands

os.environ["SSL_CERT_FILE"] = certifi.where()


# Load our token from somewhere safe
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Bot Setup
intents: Intents = Intents.default()
intents.message_content = True # NOQA
client: Client = commands.Bot(command_prefix=[">>"], intents=intents)

# deleted message holder
recentlyDeleted = "No messages have been recently deleted"

# holds all messages
allMessages = defaultdict(set)

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
        elif '>>getresult' in user_message.lower() or '>>dump' in user_message.lower():
            response: str = get_response(user_message, deleted=False, allMessages=allMessages)
        elif '>>purge' in user_message.lower(): # purging messages
            num = 2
            print("made it in the purge if block")
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


# Handling incoming messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    # adding the message to number of messages read
    addToAllMsgDictionary(message, username, user_message, channel)

    print(f'[{channel}] {username}: {user_message}')
    await send_message(message, user_message)

# adds message to the dictionary
def addToAllMsgDictionary(message: Message, username: str, user_message: str, channel:str) -> None:
        global allMessages
        allMessages[message.author.mention +"/" + username].add(f"||\"{user_message.lower()}\"||")


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
    guild = client.get_guild()
    print(client.guilds)
    
    if guild is None:
        print("Could not find guild with ID 1235744431483654144")
        return

    channel = guild.get_channel()
    
    if channel is None:
        print("Could not find channel with ID 1235744431483654147")
        return
    
    await channel.send("**BOT IS NOW LIVE!**\nCommands:\nRoll dice === generates a random number between 1-6" + 
                       "\n>>[question]? === asks a question to Llama AI. Include [###] in query to get a ### character length response"+
                       "\n>>getResult [question]? === answers a question based off of chat history")


# Main entry point
def main() -> None:
    client.run(token=TOKEN)

#lambda
def lambda_handler(event, context):
    client.run(TOKEN)

if __name__ == '__main__':
    main()

