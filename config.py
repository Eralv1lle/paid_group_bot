from dotenv import load_dotenv
from os import getenv


load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")
GROUP_ID = int(getenv("GROUP_ID"))
ADMIN_ID = int(getenv("ADMIN_ID"))