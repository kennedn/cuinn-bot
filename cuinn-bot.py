# bot.py
import os
import random
import re
from typing import final
from discord.ext import commands
from discord import Intents, Embed

token = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='.', intents=Intents.default())
#shit-posting,#planning,#hill-climbing
target_channel_ids=[991028345561042979,1082273403282665534,991028345561042980]

dog_wisdom = [
	"Bark bark, woof! (Ball is round. Round is good. Always chase the round.)",
	"Splash splash, woof woof! (Water wet. Wet is fun. No think, only jump.)",
	"Snorf snorf wag snorf! (Sniff everything twice. The same sniff may be different.)",
	"Ruff ruff, pant pant! (If you run fast enough, maybe you catch the tail this time.)",
	"Arf arf, growl woof! (Ball does not move. Stare at ball. Ball will move.)",
	"Bark woof, shlorp shlrop! (Poseidon holds no sway over my sticks.)"
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
