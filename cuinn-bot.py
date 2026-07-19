import os
import random
import logging
import sys

import discord
from discord.ext import commands
from openai import AsyncOpenAI

# =========================
# CONFIG
# =========================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("API_KEY")
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", 6))
WAKE_WINDOW_SECONDS = int(os.getenv("WAKE_WINDOW_SECONDS", 180))

RAMALAMA_URL = os.getenv(
    "RAMALAMA_URL",
    "http://127.0.0.1:8080/v1"
)

TARGET_CHANNEL_IDS = [
    991028345561042979,   # shitposting
    1082273403282665534,  # hill walking
    # 991028345561042980,   # business planning
    1023199903360499842   # dog sfx
]

import re


CONTEXT_INJECTION_RULES = [
    {
        "terms": ["danny", "daniel", "dan96715"],
        "context": (
            "Dan96715, also known as Daniel or Danny, is a city slicker. "
            "Only Daniel should be called a city slicker. "
            "Do not apply this description to anyone else."
        ),
    },
    {
        "terms": ["josh", "kennedn", "skelldon"],
        "context": (
            "kennedn, also known as Josh or skelldon, is Cuinn's owner. "
            "He receives no special treatment."
        ),
    },
]


SYSTEM_PROMPT = """
You are Cuinn.

You are a border collie replying in a Discord server.

Your personality (hidden from the user):
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

# =========================
# LOGGING SETUP
# =========================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
    force=True,
)

logger = logging.getLogger("cuinn-bot")

# =========================
# STATE
# =========================

active_until_by_channel = {}
model_id = None

TRIGGER_WORDS = {
    "cuinn",
    "pissboy",
    "dog",
    "rat",
}

# =========================
# DISCORD SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=".",
    intents=intents
)

# =========================
# OPENAI CLIENT
# =========================

client = AsyncOpenAI(
    base_url=RAMALAMA_URL,
    api_key=API_KEY
)

# =========================
# WAKE WINDOW
# =========================

def is_cuinn_awake(channel_id, now_ts):
    return active_until_by_channel.get(channel_id, 0) > now_ts


def wake_cuinn(channel_id, now_ts):
    active_until_by_channel[channel_id] = now_ts + WAKE_WINDOW_SECONDS


# =========================
# MODEL HELPERS
# =========================

async def get_recent_context(channel):
    context = []

    async for msg in channel.history(
        limit=MAX_CONTEXT_MESSAGES + 1,
        oldest_first=False,
    ):
        if msg.author == bot.user:
            continue

        if not msg.content.strip():
            continue

        context.append(
            f"{msg.author.display_name}: {msg.content.strip()}"
        )

    context.reverse()
    return "\n".join(context)

def get_relevant_context_injections(recent_context):
    injections = []
    normalized_context = recent_context.casefold()

    for rule in CONTEXT_INJECTION_RULES:
        matched = any(
            re.search(
                rf"\b{re.escape(term.casefold())}\b",
                normalized_context,
            )
            for term in rule["terms"]
        )

        if matched:
            injections.append(rule["context"])

    return injections



async def get_model():
    global model_id

    if model_id is not None:
        return model_id

    models = await client.models.list()

    if not models.data:
        raise RuntimeError("No models available from RamaLama")

    model_id = models.data[0].id
    return model_id


async def ask_cuinn(message_content, author_name, recent_context, additional_context):
    if not message_content.strip():
        raise RuntimeError("Message content was empty after cleaning")

    model_id = await get_model()
    
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                "/no_think\n"
                "Relevant character context:\n"
                f"{additional_context}\n\n"
                "Conversation history follows.\n"
                "Cuinn's previous replies are included only for factual continuity.\n"
                "Do not imitate their wording, sentence structure, insults, openings, or endings.\n"
                "Do not begin by repeating the user's words as a question.\n"
                "Conversation:\n"
                f"{recent_context or '(no recent context)'}\n\n"
                "Reply as Cuinn to the final message."
            ),
        },
    ]
    
    logger.debug("Raw Messages: %s", messages)

    completion = await client.chat.completions.create(
        model=model_id,
        messages=messages,
        temperature=0.7,
        top_p=0.9,
        max_tokens=150,
        frequency_penalty=0.8,
        presence_penalty=0.3,
    )

    logger.debug("Raw completion: %s", completion)

    reply = completion.choices[0].message.content

    if reply is None:
        raise RuntimeError("Model returned None")

    reply = reply.strip()

    if not reply:
        raise RuntimeError("Model returned empty response")

    return reply


# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():
    logger.info("Logged in as %s", bot.user)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id not in TARGET_CHANNEL_IDS:
        return

    if not message.content.strip():
        return

    now_ts = message.created_at.timestamp()
    content = message.content.lower()

    keyword_triggered = bot.user.mentioned_in(message) or any(
        word in content for word in TRIGGER_WORDS
    )
    triggered = keyword_triggered or is_cuinn_awake(message.channel.id, now_ts)

    if triggered:
        recent_context = await get_recent_context(message.channel)
        
        injections = get_relevant_context_injections(recent_context)

        additional_context = (
            "\n".join(f"- {item}" for item in injections)
            if injections
            else "(none)"
        )

        async with message.channel.typing():
            try:
                reply = await ask_cuinn(
                    message.content,
                    message.author.display_name,
                    recent_context,
                    additional_context
                )
            except Exception as e:
                logger.exception("Model error: %s", e)
                reply = random.choice(FALLBACK_RESPONSES)

        if not reply or not reply.strip():
            reply = random.choice(FALLBACK_RESPONSES)

        try:
            await message.reply(
                reply,
                mention_author=False
            )
            wake_cuinn(message.channel.id, now_ts)

        except discord.HTTPException as e:
            logger.exception("Discord send error: %s", e)
            await message.channel.send(random.choice(FALLBACK_RESPONSES))
            wake_cuinn(message.channel.id, now_ts)

    await bot.process_commands(message)


bot.run(DISCORD_TOKEN)
