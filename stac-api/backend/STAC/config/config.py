from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

import yaml

def load_config() -> dict:
    with open('config/config.yml') as yaml_file:
        conf = yaml.load(yaml_file.read(), Loader=yaml.SafeLoader)
    return conf

CONF = load_config()

host1 = os.getenv("HOST")
port1 = os.getenv("PORT")
username1 = os.getenv("USER")
password1 = os.getenv("PASSWORD")

DB_CLIENT = AsyncIOMotorClient(
    host = host1,
    port = int(port1),
    username = username1,
    password = password1,
)

DB = DB_CLIENT[CONF.get("databases", dict())["default"]["NAME"]]

def close_db_client():
    DB_CLIENT.close()

