# -*- coding: utf-8 -*-
import random
import time
import re
from telethon import TelegramClient, events, Button
from db import get_user, update_user, update_grow_time  # Import database functions
import redis

# Bot credentials
API_ID = 23379629
API_HASH = "5cec6762c78e140d804a6226f87ab4a8"
BOT_TOKEN = "7896510782:AAF5i1WCRRKsxDMZ6YidAAoDNhAJL6k2nfY"

# Initialize the Redis client
REDIS_HOST = "picked-bengal-10585.upstash.io"
REDIS_PORT = 6379
REDIS_PASSWORD = "ASlZAAIjcDFlYTVjZDgwZWIwNzc0OWU0YmU4OGExOTViYTNmMTNmM3AxMA"
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    ssl=True,
    decode_responses=True
)

# Initialize the bot
client = TelegramClient("pussy_grow_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    user_id = event.sender_id
    username = event.sender.username if event.sender.username else "Stranger"
    
    # Check if user data already exists in Redis
    user = get_user(user_id)
    if not user:
        # If user doesn't exist in Redis, store their data
        redis_client.hset(f"user:{user_id}", "pussy_size", 5)  # Default size
        redis_client.hset(f"user:{user_id}", "last_grow", 0)  # Initial last grow time
    
    # Sarcastic greeting
    greeting_message = f"Welcome to **Pussy Grower Bot**, @{username}! Get your pussy fuked by random niggas to grow it.  Please start the bot in **Personal** to use it without any problems."
    
    await event.reply(greeting_message)
    
# /grow command
@client.on(events.NewMessage(pattern="/grow"))
async def grow(event):
    user_id = event.sender_id
    user = get_user(user_id)
    current_time = time.time()

    if user and current_time - user[1] < 28800:  # 8 hours = 28800 seconds
        await event.reply(" Oh, come on! Youre trying to take another **Dick** again so soon? Slow down, niggaa! 8 hours, remember?")
        return

    # New users or existing users grow by +1 to +8 cm
    size_change = random.randint(1, 8)
    new_size = update_user(user_id, size_change)
    update_grow_time(user_id, current_time)

    await event.reply(f" Congratulations!! You just took 13 dicks, your pussy is heavily stretched, it's now +{size_change}cm! Your pussy is now: {new_size}cm.")

# /size command – Check current pussy size
@client.on(events.NewMessage(pattern="/size"))
async def check_size(event):
    user_id = event.sender_id
    user = get_user(user_id)

    if not user:
        await event.reply(" You are virgin yet, take some dicks in your tight pussy first. Use /grow and fill your pussy with dicks.")
    else:
        await event.reply(f" Your current pussy size is **{user[0]}cm**.")

# /fight command – Start a fight
@client.on(events.NewMessage(pattern=r"/fight (\d+)"))
async def fight(event):
    attacker_id = event.sender_id
    amount = int(event.pattern_match.group(1))

    attacker = get_user(attacker_id)
    if not attacker or attacker[0] < amount:
        await event.reply(" Your pussy is too small. Use /loan to take more dick!")
        return

    fight_msg = await event.reply(
        f" @{event.sender.username} is challenging for {amount}cm! Click **Attack** to fight!",
        buttons=[Button.inline(" Attack", f"fight|{attacker_id}|{amount}")]
    )

import random

@client.on(events.CallbackQuery(pattern=r"fight\|(\d+)\|(\d+)"))
async def handle_fight(event):
    try:
        data = event.data.decode().split("|")
        if len(data) != 3:
            await event.answer(" Invalid fight data!", alert=True)
            return

        attacker_id, amount = map(int, data[1:])
        defender_id = event.sender_id

        if attacker_id == defender_id:
            await event.answer(" You can't fight yourself!", alert=True)
            return

        attacker = get_user(attacker_id)
        defender = get_user(defender_id)

        if not attacker or not defender:
            await event.answer(" One of the fighters doesn't exist!", alert=True)
            return

        if defender[0] < amount:
            await event.answer(" Your pussy is too small for this fight! Use /loan to take more dick!", alert=True)
            return

        # Probability-based winner decision
        attacker_size = attacker[0]
        defender_size = defender[0]

        if attacker_size > defender_size:
            attacker_chance = 60  # 60% chance if attacker has a bigger size
        elif defender_size > attacker_size:
            attacker_chance = 40  # 40% chance if defender is bigger
        else:
            attacker_chance = 50  # Equal fight, 50-50 chance

        # Adding a small random factor (5% variation)
        attacker_chance += random.randint(-5, 5)
        defender_chance = 100 - attacker_chance  # Defender gets the remaining probability

        winner_id = random.choices([attacker_id, defender_id], [attacker_chance, defender_chance])[0]
        loser_id = attacker_id if winner_id == defender_id else defender_id

        # Prevent loser from going negative
        new_loser_size = max(0, defender[0] - amount) if loser_id == defender_id else max(0, attacker[0] - amount)

        update_user(winner_id, amount)  # Increase size for winner
        update_user(loser_id, -amount)  # Deduct size from loser

        # Fetch usernames or fallback to first name
        winner_entity = await client.get_entity(winner_id)
        loser_entity = await client.get_entity(loser_id)

        winner_name = f"@{winner_entity.username}" if winner_entity.username else winner_entity.first_name
        loser_name = f"@{loser_entity.username}" if loser_entity.username else loser_entity.first_name

        await event.edit(f" **Fight Result:** {winner_name} won **{amount}cm**!\n"
                         f" Winner: {winner_name} (+{amount}cm)\n"
                         f" Loser: {loser_name} (-{amount}cm)")
    except Exception as e:
        print(f"Error in handle_fight: {e}")
        
        
@client.on(events.NewMessage(pattern="/loan"))
async def loan(event):
    user_id = event.sender_id
    user = get_user(user_id)

    if not user:
        await event.reply("You don't need more dicks, your pussy is already filled! Grow some more first.")
        return

    current_size = user[0]
    last_grow_time = user[1]
    current_time = time.time()

    # Check if the user has 0 cm or less (to be eligible for a loan)
    if current_size > 0:
        await event.reply("You are not eligible for a more Dicks. Dixks are only available if your pussy is shrinked.")
        return

    # Check if the loan was taken in the last 8 hours
    loan_cooldown = 28800  # 8 hours in seconds
    if current_time - last_grow_time < loan_cooldown:
        await event.reply(" You Just took multiple dicks wait 8 hours. else your **Pussy** will explode!")
        return

    # Grant the loan (8 cm)
    loan_amount = 8
    new_size = current_size + loan_amount  # Add the loan amount

    # Update the user's size (but DO NOT update grow time)
    update_user(user_id, new_size)  # Update size correctly

    # Send confirmation message
    await event.reply(f"Congratulations! You've been granted a loan of 8 cm. Your current size is now {new_size} cm.")

from telethon.tl.types import PeerUser

@client.on(events.NewMessage(pattern="/broadcast (.+)"))
async def broadcast(event):
    # Ensure the user is an admin (you can change this condition as needed)
    if event.sender_id != 7071147081:  # Replace with your admin ID
        await event.reply("You are not authorized to use this command.")
        return
    
    # Extract the broadcast message (everything after /broadcast)
    broadcast_message = event.pattern_match.group(1)

    # Get all user IDs who started the bot
    user_ids = redis_client.keys("user:*")  # All keys in Redis with pattern "user:<user_id>"
    
    # Extract user IDs and send the custom broadcast message to each user
    for user_key in user_ids:
        user_key_str = user_key.decode("utf-8") if isinstance(user_key, bytes) else user_key
        user_id = user_key_str.split(":")[1]  # Extract the user ID from the key

        try:
            # Send the custom broadcast message to the user
            await client.send_message(int(user_id), broadcast_message)
        except Exception as e:
            print(f"Failed to send message to {user_id}: {e}")
    
    await event.reply("Broadcast message has been sent to all users.")
    
@client.on(events.NewMessage(pattern="/top"))
async def top(event):
    

    # Get all user IDs and their pussy sizes from Redis
    user_ids = redis_client.keys("user:*")  # All keys in Redis with pattern "user:<user_id>"

    # Create a list to store user data
    users_data = []

    for user_key in user_ids:
        # Make sure we're working with the correct type
        if isinstance(user_key, bytes):  # If user_key is a byte string, decode it
            user_key = user_key.decode()

        user_id = user_key.split(":")[1]  # Extract user ID from the key
        pussy_size = int(redis_client.hget(user_key, "pussy_size"))  # Get pussy size

        # Try to get the username or name using get_entity (it might throw an error if user is not available)
        try:
            user_entity = await client.get_entity(int(user_id))  # Convert to integer if it's in string format
            if user_entity.username:
                username = user_entity.username
            else:
                # If no username, use the user's first name
                username = user_entity.first_name if user_entity.first_name else "No Name"
        except ValueError:
            # Handle invalid user ID or other errors gracefully
            username = "Unknown User"
        except Exception as e:
            # Catch any other unexpected errors and log them
            print(f"Error fetching username for {user_id}: {str(e)}")
            username = "Unknown User"

        # Append the user data to the list
        users_data.append((username, pussy_size))

    # Sort the list by pussy size in descending order
    users_data.sort(key=lambda x: x[1], reverse=True)

    # Limit the result to top 5 (or fewer if there aren't enough users)
    top_users = users_data[:5]

    # Create the message with top users
    top_message = " **Top Pussy Sizes** \n\n"
    for idx, (username, pussy_size) in enumerate(top_users, start=1):
        top_message += f"#{idx} @{username} - {pussy_size}cm\n"

    # Send the top users list as a reply
    await event.reply(top_message)
@client.on(events.NewMessage(pattern=r"/gift (\d+) (\d+)"))
async def gift(event):
    admin_id = 7071147081  # Replace with your actual admin ID
    sender_id = event.sender_id

    # Check if the sender is the admin
    if sender_id != admin_id:
        await event.reply(" You are not authorized to use this command.")
        return

    # Extract user ID and size from the command
    match = re.match(r"/gift (\d+) (\d+)", event.raw_text)
    if not match:
        await event.reply(" Invalid format! Use: `/gift <user_id> <size>`")
        return

    user_id = int(match.group(1))
    gift_size = int(match.group(2))

    # Fetch the user
    user = get_user(user_id)
    if not user:
        await event.reply(" User not found in the database.")
        return

    # Update the user's size
    new_size = user[0] + gift_size
    update_user(user_id, new_size)

    # Confirm the gift
    await event.reply(f" Successfully gifted {gift_size} cm to user {user_id}. Their new size is {new_size} cm.")

    # Notify the user
    try:
        await client.send_message(user_id, f" You have received a gift of {gift_size} cm! Your new size is {new_size} cm.")
    except:
        await event.reply(" Could not notify the user (they might have blocked the bot).")
    
# Start bot
print(" Pussy Grow Bot is running...")
client.run_until_disconnected()