from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response
import certifi
import asyncio

os.environ["SSL_CERT_FILE"] = certifi.where()


# Load our token from somewhere safe
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Bot Setup
intents: Intents = Intents.default()
intents.message_content = True # NOQA
client: Client = Client(intents=intents)


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
        if deleted:
            response: str = get_response(user_message, deleted=True)
        else:
            response: str = get_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
        
        # if a question is asked to the chatbot, sleep for 5 seconds to ensure the AI model isn't overloaded because of server requests 
        # as it is hosted on the Hugging Facec Inference API
    
        # if '>>' in user_message:
            # processing_messages = False
            # sleepTime: str = "Not processing any messages for the next 5 seconds..."
            # await message.author.send(sleepTime) if is_private else await message.channel.send(sleepTime)
            # await asyncio.sleep(5)
            # processing_messages = True
            # await message.author.send("Im back!") if is_private else await message.channel.send("Im back!")
    except Exception as e:
        print(e)


# Handling the startup for our bot
@client.event
async def on_read(message: Message) ->None:
    print(f'{client.user} is now running!')
    await send_message(message, "Bot is now live!")

# Status update of the bot when it first goes live
@client.event
async def on_ready():
    print("BOT IS NOW LIVE!")

# Handling incoming messages
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: {user_message}')
    await send_message(message, user_message)

# Detects deleted messages
@client.event
async def on_message_delete(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    user_message = f'<-DELETED->[{channel}] {username}: {user_message}'
    print(user_message)

    await send_message(message, user_message, deleted=True)

# Main entry point
def main() -> None:
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()
