# Yaple - Discord Wordle Bot

Yaple is a Discord bot that brings the Wordle game to your server. Users can play daily Wordle, track their stats, view their boards, and compare results with others.

## Commands

- Daily Wordle game for each user
- `/guess <word>`: Make a guess
- `/board`: View your current board
- `/stats <user>`: See yours or another user's stats
- `/used`: See your used letters
- `/yapple`: See who completed today's Wordle

## Installation

### Prerequisites

- Docker
- Discord account

### 1. Clone the repository
`mkdir yaple`
`cd yaple`
`git clone https://github.com/lucylamb0/Yaple.git`

### 2. Create a `.env` file

Add your Discord bot token to a file named `.env` in the project root: (SECRET="YOURTOKEN"):

### 3. Build and run the Docker container
Use `docker build -t <bot_name>`
`docker run <bot_name>`

## Discord Developer Portal Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name it (e.g., Yaple)
3. Go to "Bot" section, click "Add Bot"
4. Copy the bot token and add it to your `.env` file
5. Go to "OAuth2" > "URL Generator"
   - Select `bot` and `applications.commands` scopes
   - Under "Bot Permissions", select `Send Messages`, `Read Message History`, `Add Reactions` and `View Channels`
6. Copy the generated URL and use it to invite the bot to your server
