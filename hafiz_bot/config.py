import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID") # @ChannelName or ID
CHANNEL_URL = os.getenv("CHANNEL_URL") # https://t.me/ChannelName
ADMIN_GROUP_ID = os.getenv("ADMIN_GROUP_ID") # Group ID for verification
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
