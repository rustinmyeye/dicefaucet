import logging
import sqlite3
import random
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext
from ergpy import appkit, helper_functions

# Configuration
BOT_TOKEN = 'your_bot_token_goes_here'
DICE_SIDES = 9
WINNING_NUMBERS = [6, 9]
ROLL_COOLDOWN_MINUTES = 120  # Cooldown period in minute
ROLLS_BEFORE_COOLDOWN = 2  # Number of rolls allowed before cooldown
MNEMONIC = "your_seed_phrase_here"
TOKEN_ID = "token_id"
BOT_WALLET_ADDRESS = "your_wallet_address_associated_with_the_seed"


# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Create or connect to the SQLite databases
conn = sqlite3.connect('users.db')
c_users = conn.cursor()

# Create tables if they dont exist for users
c_users.execute('''CREATE TABLE IF NOT EXISTS users
                   (user_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT)''')
conn.commit()

conn_wallets = sqlite3.connect('wallets.db')
c_wallets = conn_wallets.cursor()

# Create tables if they don't exist for wallets
c_wallets.execute('''CREATE TABLE IF NOT EXISTS wallets
                     (user_id INTEGER PRIMARY KEY, wallet_address TEXT)''')
conn_wallets.commit()

conn_rolls = sqlite3.connect('rolls.db')
c_rolls = conn_rolls.cursor()

# Create tables if they don't exist for rolls
c_rolls.execute('''CREATE TABLE IF NOT EXISTS rolls
                   (user_id INTEGER PRIMARY KEY, roll_count INTEGER DEFAULT 0, last_roll_date TEXT)''')
conn_rolls.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    explanation = ("I'm an alien bot that allows you to roll a dice and potentially win 👽 tokens. Rolling a 6 or 9 is nice. Here are the available commands:\n"
                   "/alien - Display this help message\n"
                   "/roll - Roll the dice and try your luck\n"
                   "/register <walletaddress> - Register your Ergo wallet address\n"
                   "/list - Check the registered wallet address\n"
                   "/update <walletaddress> - Update the registered wallet address\n"
                   "/delete - Delete the registered wallet address")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=explanation)

import asyncio

async def roll(update: Update, context: CallbackContext) -> None:
    # Introduce a delay of 3 seconds
    await asyncio.sleep(3)

    user_id = update.effective_user.id

    # Get the current time
    now = datetime.datetime.now()

    # Get the roll count and last roll date for the user
    c_rolls.execute("SELECT roll_count, last_roll_date FROM rolls WHERE user_id=?", (user_id,))
    roll_info = c_rolls.fetchone()

    # Initialize the roll count and last roll date if the user is new
    if not roll_info:
        roll_count = 0
        last_roll_date = None
    else:
        roll_count, last_roll_date_str = roll_info
        # Check if last_roll_date_str is not None and has valid format
        if last_roll_date_str:
            try:
                # Convert last_roll_date string to datetime object
                last_roll_date = datetime.datetime.strptime(last_roll_date_str, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                last_roll_date = None
        else:
            last_roll_date = None

    # Check if the user has reached the roll limit and is within the cooldown period
    if roll_count >= ROLLS_BEFORE_COOLDOWN and last_roll_date and now < last_roll_date + datetime.timedelta(minutes=ROLL_COOLDOWN_MINUTES):
        # Calculate remaining cooldown time
        remaining_time = (last_roll_date + datetime.timedelta(minutes=ROLL_COOLDOWN_MINUTES)) - now
        minutes = max(remaining_time.seconds // 60, 1)  # Ensure at least 1 minute remaining
        await update.message.reply_text(f"You can roll again in {minutes} minute{'s' if minutes > 1 else ''}.")
        return

    # Roll the dice
    roll_result = random.randint(1, DICE_SIDES)

    # Increment the roll count
    roll_count += 1

    # Set response based on roll result
    if roll_result == 6:
        aliens = random.randint(1, 100)
        await update.message.reply_text(f"You rolled a {roll_result}, so you've won: {aliens} alien!")
        user_wallet_address = wallet_address
        output_main = helper_functions.send_token(
            ergo=ergo,
            amount=[0.0001],
            amount_tokens=[[aliens]],
            receiver_addresses=[user_wallet_address],
            tokens=[[TOKEN_ID]],
            wallet_mnemonic=MNEMONIC
        )
        print(output_main)

    elif roll_result == 9:
        aliens = random.randint(100, 1000)
        await update.message.reply_text(f"You rolled a {roll_result}, so you've won: {aliens} alien!")
        user_wallet_address = wallet_address
        output_main = helper_functions.send_token(
            ergo=ergo,
            amount=[0.0001],
            amount_tokens=[[aliens]],
            receiver_addresses=[user_wallet_address],
            tokens=[[TOKEN_ID]],
            wallet_mnemonic=MNEMONIC
        )
        print(output_main)

    else:
        await update.message.reply_text(f"You rolled a {roll_result}, loser!")

    # Reset the roll count and update the last roll date for the user after the cooldown period
    if last_roll_date and now >= last_roll_date + datetime.timedelta(minutes=ROLL_COOLDOWN_MINUTES):
        roll_count = 0

    # Update the roll count and last roll date for the user
    c_rolls.execute("INSERT OR REPLACE INTO rolls (user_id, roll_count, last_roll_date) VALUES (?, ?, ?)",
                    (user_id, roll_count, now))
    conn_rolls.commit()

async def register(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text("Please enter your Ergo wallet address after the /register command.")
        return
    
    wallet_address = context.args[0]
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    last_name = update.effective_user.last_name

    # Save the user info and wallet address to the database
    c_users.execute("INSERT OR REPLACE INTO users (user_id, first_name, last_name) VALUES (?, ?, ?)", (user_id, first_name, last_name))
    c_wallets.execute("INSERT OR REPLACE INTO wallets (user_id, wallet_address) VALUES (?, ?)", (user_id, wallet_address))
    conn.commit()
    conn_wallets.commit()
    
    await update.message.reply_text(f"Your Ergo wallet address has been registered: {wallet_address}")

# ... [rest of the code for list_wallet, update_wallet, delete_wallet]
async def list_wallet(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    c_wallets.execute("SELECT wallet_address FROM wallets WHERE user_id=?", (user_id,))
    wallet_address = c_wallets.fetchone()

    if wallet_address:
        await update.message.reply_text(f"Your registered Ergo wallet address is: {wallet_address[0]}")
    else:
        await update.message.reply_text("You have not registered a wallet address yet.")

async def update_wallet(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text("Please enter your new Ergo wallet address after the /update command.")
        return
    
    new_wallet_address = context.args[0]
    user_id = update.effective_user.id

    c_wallets.execute("UPDATE wallets SET wallet_address=? WHERE user_id=?", (new_wallet_address, user_id))
    conn_wallets.commit()

    await update.message.reply_text(f"Your Ergo wallet address has been updated to: {new_wallet_address}")

async def delete_wallet(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    c_wallets.execute("DELETE FROM wallets WHERE user_id=?", (user_id,))
    conn_wallets.commit()

    await update.message.reply_text("Your registered Ergo wallet address has been deleted.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    start_handler = CommandHandler('alien', start)
    roll_handler = CommandHandler('roll', roll)
    register_handler = CommandHandler('register', register)
    list_wallet_handler = CommandHandler('list', list_wallet)
    update_wallet_handler = CommandHandler('update', update_wallet)
    delete_wallet_handler = CommandHandler('delete', delete_wallet)

    application.add_handler(start_handler)
    application.add_handler(roll_handler)
    application.add_handler(register_handler)
    application.add_handler(list_wallet_handler)
    application.add_handler(update_wallet_handler)
    application.add_handler(delete_wallet_handler)
    
    application.run_polling()
