# bot.py
import os
import random
import re
from typing import final
from discord.ext import commands
from discord import Intents, Embed

token = os.getenv('DISCORD_TOKEN')
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)
#shit-posting,#planning,#hill-climbing
target_channel_ids=[991028345561042979,1082273403282665534,991028345561042980]

dog_wisdom = [
"Fuckin Gook"
#    "Yeah, that’s happening, mate. Might take a while, but I’ll get there... eventually... after a few more drinks.",
#    "Nah, not a chance. Don’t even bother. I’m not interested, unless you’ve got snacks.",
#    "Could be, could be not. I’m too pissed to make up my mind, but let’s see how things go... if I don’t pass out first.",
#    "You’re askin’ a dog who’s half-cut, mate. Gimme a minute and I might have a proper answer... or not.",
#    "Yeah, but only if you scratch my belly first, mate. I’m not cheap, y’know. Gotta earn that ‘yes.’",
#    "Bit hazy on that one. Could go either way, but who cares, I’m just here for a good time.",
#    "Yeah, most likely. But don’t get too excited—could be a drunken mess by the time we get there.",
#    "Nah, mate, that’s not happening. You’re better off trying something else. Trust me, I’ve been down this road.",
#    "No bloody way. I wouldn’t do that even if you paid me in treats. Not today, mate!",
#    "Could be, might not be. I’d say flip a coin, but I’m too busy sniffin’ around for snacks.",
#    "Nah, not a good idea, mate. Save yourself the trouble and have another drink instead. Trust me.",
#    "Hard to say, I’m halfway into my third beer. Give me a minute and I’ll probably forget what you asked.",
#    "Nah, mate, don’t get your hopes up. You’re better off with a dog that’s more sober than me.",
#    "Too blurry to tell, mate. But I’ll probably end up chasing my tail in a minute—so, maybe that’s a yes?",
#    "Ugh, mate, I’ve had a few too many to think straight. Give me a snack, and we’ll talk about it later."
]

@bot.event
async def on_message(message):
    # Check if the message is from the bot itself to prevent self-replies
    if message.author == bot.user:
        return

    # Check if the message is in a target channel and if the bot is mentioned or if the message contains "cuinn" or "dogboy"
    if message.channel.id not in target_channel_ids:
        return
    if bot.user.mentioned_in(message) or 'cuinn' in message.content.lower() or 'pissboy' in message.content.lower():
        await message.channel.send(random.choice(dog_wisdom))

    # Process commands if needed
    await bot.process_commands(message)

bot.run(token)
