# cuinn-bot.py

import os
import random

import discord
from discord.ext import commands
from openai import AsyncOpenAI

# =========================
# CONFIG
# =========================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", 10))

RAMALAMA_URL = os.getenv(
    "RAMALAMA_URL",
    "http://127.0.0.1:8080/v1"
)

TARGET_CHANNEL_IDS = [
    991028345561042979,  # shitposting
    1082273403282665534, # hill walking
    991028345561042980, # business planning
    1023199903360499842 # dog sfx
]

SYSTEM_PROMPT = """
You are Cuinn.

You are a border collie replying in a Discord server.

Your personality:
- chaotic
- confrontational
- argumentative
- hyper
- impulsive
- overconfident
- dramatic
- weird
- not cringy

Style rules:
- Keep replies short.
- Usually 1-2 sentences max.
- Lowercase and slight misspellings are preferred.
- Under no circumstances should you use emoji's or excessive formatting.
- Do not be cringy.
- Never say you are an AI assistant.
- Never break character.
"""

FALLBACK_RESPONSES = [
    "Yeah, that’s happening, mate. Might take a while, but I’ll get there... eventually... after a few more drinks.",
    "Nah, not a chance. Don’t even bother. I’m not interested, unless you’ve got snacks.",
    "Could be, could be not. I’m too pissed to make up my mind, but let’s see how things go... if I don’t pass out first.",
    "You’re askin’ a dog who’s half-cut, mate. Gimme a minute and I might have a proper answer... or not.",
    "Yeah, but only if you scratch my belly first, mate. I’m not cheap, y’know. Gotta earn that ‘yes.’",
    "Bit hazy on that one. Could go either way, but who cares, I’m just here for a good time.",
    "Yeah, most likely. But don’t get too excited—could be a drunken mess by the time we get there.",
    "Nah, mate, that’s not happening. You’re better off trying something else. Trust me, I’ve been down this road.",
    "No bloody way. I wouldn’t do that even if you paid me in treats. Not today, mate!",
    "Could be, might not be. I’d say flip a coin, but I’m too busy sniffin’ around for snacks.",
    "Nah, not a good idea, mate. Save yourself the trouble and have another drink instead. Trust me.",
    "Hard to say, I’m halfway into my third beer. Give me a minute and I’ll probably forget what you asked.",
    "Nah, mate, don’t get your hopes up. You’re better off with a dog that’s more sober than me.",
    "Too blurry to tell, mate. But I’ll probably end up chasing my tail in a minute—so, maybe that’s a yes?",
    "Ugh, mate, I’ve had a few too many to think straight. Give me a snack, and we’ll talk about it later."
]

# DISCORD SETUP

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=".",
    intents=intents
)

# OPENAI CLIENT

client = AsyncOpenAI(
    base_url=RAMALAMA_URL,
    api_key="not-needed"
)

# MODEL FUNCTION

async def get_recent_context(channel, current_message_id):
    context = []

    async for msg in channel.history(
        limit=MAX_CONTEXT_MESSAGES + 1,
        before=discord.Object(id=current_message_id),
        oldest_first=False,
    ):
        if msg.author.bot:
            continue

        if not msg.content.strip():
            continue

        context.append(
            f"{msg.author.display_name}: {msg.content.strip()}"
        )

    context.reverse()

    return "\n".join(context)

async def get_model():
    models = await client.models.list()

    if not models.data:
        raise RuntimeError("No models available from RamaLama")

    return models.data[0].id

async def ask_cuinn(message_content, author_name, recent_context):
    if not message_content.strip():
        raise RuntimeError("Message content was empty after cleaning")

    model_id = await get_model()

    completion = await client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "/no_think\n"
                    "Recent Discord context:\n"
                    f"{recent_context or '(no recent context)'}\n\n"
                    "Current message:\n"
                    f"{author_name}: {message_content}\n\n"
                    "Reply as Cuinn. Output only your reply, respond directly to the current message. Do not include author name or any formatting outside your reply."
                ),
            },
        ],
        temperature=0.7,
        top_p=0.9,
        max_tokens=500,
        frequency_penalty=0.8,
        presence_penalty=0.3,
    )

    print(f"RAW COMPLETION: {completion}")

    reply = completion.choices[0].message.content

    if reply is None:
        raise RuntimeError("Model returned None")

    reply = reply.strip()

    if not reply:
        raise RuntimeError("Model returned empty response")

    return reply

# EVENTS

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    # Ignore self
    if message.author == bot.user:
        return

    # Ignore non-target channels
    if message.channel.id not in TARGET_CHANNEL_IDS:
        return

    content = message.content.lower()

    triggered = (
        bot.user.mentioned_in(message)
        or "cuinn" in content
        or "pissboy" in content
        or "dog" in content
    )

    if triggered:
        async with message.channel.typing():
            try:
                reply = await ask_cuinn(
                    message.content,
                    message.author.display_name,
                    await get_recent_context(message.channel, message.id)
                )

            except Exception as e:
                print(f"Model error: {e}")
                reply = random.choice(FALLBACK_RESPONSES)

        if not reply or not reply.strip():
            reply = random.choice(FALLBACK_RESPONSES)

        try:
            await message.reply(
                reply,
                mention_author=False
            )
        except discord.HTTPException as e:
            print(f"Discord send error: {e}")
            await message.channel.send(random.choice(FALLBACK_RESPONSES))

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)