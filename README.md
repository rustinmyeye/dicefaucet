# Dice Faucet Telegram Bot

This Telegram bot allows users to roll a dice and potentially win tokens. It is integrated with ergpy to distribute tokens to winners. Users can register their Ergo wallet addresses to receive tokens upon winning.

## Features

- Roll a dice with `/roll` command.
- Register, update, or delete your Ergo wallet address.
- Check your registered wallet address with `/list` command.
- Detailed help message with `/alien` command.

## Configuration

Before running the bot, make sure to configure the following settings in the script:
- `BOT_TOKEN`: Telegram bot token obtained from BotFather.
- `DICE_SIDES`: Number of sides on the dice.
- `WINNING_NUMBERS`: List of winning numbers.
- `ROLL_COOLDOWN_MINUTES`: Cooldown period in minutes between rolls.
- `ROLLS_BEFORE_COOLDOWN`: Number of rolls allowed before cooldown.
- `MNEMONIC`: Seed phrase for the wallet.
- `TOKEN_ID`: ID of the token to be distributed.
- `BOT_WALLET_ADDRESS`: Wallet address associated with the seed phrase.

## Installation

Before you begin, ensure you have git and python installed, then:

1. Clone the repository:

```bash
git clone https://github.com/rustinmyeye/dicefaucet.git
```
2. Navigate to the cloned repository directory
```
cd dicefaucet
```
3. Install the required dependencies
```
pip install -r requirements.txt
```

## Run It

```
python dicefaucet.py
```
