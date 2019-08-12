import logging
import os
import sys
import re
import requests

from pyrogram import Client, errors
from pydrive.auth import GoogleAuth

# Postgresql
import threading

from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func, distinct, Column, String, UnicodeText, Integer

# logging
# 
# -> Advanced logging, for debugging purposes
# LOG_FORMAT = "[%(asctime)s.%(msecs)03d] %(filename)s:%(lineno)s %(levelname)s: %(message)s"
# logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
# 
logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    log.error("You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting.")
    quit(1)

try:
	from nana.config import Development as Config
except ModuleNotFoundError:
	log.error("You need to place config.py in nana dir!")
	quit(1)

USERBOT_VERSION = "0.3.2"
ASSISTANT_VERSION = "0.3.2"

OFFICIAL_BRANCH = ('master', 'dev', 'asyncio')
REPOSITORY = "https://github.com/AyraHikari/Nana-TgBot"
RANDOM_STICKERS = ["CAADAgAD6EoAAuCjggf4LTFlHEcvNAI", "CAADAgADf1AAAuCjggfqE-GQnopqyAI", "CAADAgADaV0AAuCjggfi51NV8GUiRwI"]

ENV = bool(os.environ.get('ENV', False))

if ENV:
	# Version
	lang_code = os.environ.get('lang_code', "en")
	device_model = os.environ.get('device_model', "PC")
	app_version = "💝 Nana v{}".format(USERBOT_VERSION)
	system_version = os.environ.get('system_version', "Linux")

	# Must be filled
	api_id = os.environ.get('api_id', None)
	api_hash = os.environ.get('api_hash', None)

	# Required for some features
	# Set temp var for load later
	Owner = 0
	OwnerName = ""
	OwnerUsername = ""
	BotID = 0
	BotName = ""
	BotUsername = ""
	# From config
	Command = eval(os.environ.get('Command', '["!", ".", "-", "^"]'))
	NANA_WORKER = int(os.environ.get('NANA_WORKER', 8))
	ASSISTANT_WORKER = int(os.environ.get('ASSISTANT_WORKER', 2))

	try:
		TEST_DEVELOP = bool(os.environ.get('TEST_DEVELOP', False))
		if TEST_DEVELOP:
			BOT_SESSION = os.environ.get('BOT_SESSION', None)
			APP_SESSION = os.environ.get('APP_SESSION', None)
			log.info("Testing mode activated!")
		else:
			raise AttributeError
	except AttributeError:
		BOT_SESSION = "nana/session/ManageBot"
		APP_SESSION = "nana/session/Nana"

	# APIs
	thumbnail_API = os.environ.get('thumbnail_API', None)
	screenshotlayer_API = os.environ.get('screenshotlayer_API', None)

	# LOADER
	USERBOT_LOAD = eval(os.environ.get('USERBOT_LOAD', "[]"))
	USERBOT_NOLOAD = eval(os.environ.get('USERBOT_NOLOAD', "[]"))
	ASSISTANT_LOAD = eval(os.environ.get('ASSISTANT_LOAD', "[]"))
	ASSISTANT_NOLOAD = eval(os.environ.get('ASSISTANT_NOLOAD', "[]"))

	DB_URL = os.environ.get('DB_URL', None)
	ASSISTANT_BOT = os.environ.get('ASSISTANT_BOT', False)
	ASSISTANT_BOT_TOKEN = os.environ.get('ASSISTANT_BOT_TOKEN', None)
	AdminSettings = eval(os.environ.get('AdminSettings', "[]"))
	REMINDER_UPDATE = bool(os.environ.get('REMINDER_UPDATE', True))
	TEST_MODE = bool(os.environ.get('TEST_MODE', False))
else:
	# Version
	lang_code = Config.lang_code
	device_model = Config.device_model
	app_version = "💝 Nana v{}".format(USERBOT_VERSION)
	system_version = Config.system_version

	# Must be filled
	api_id = Config.api_id
	api_hash = Config.api_hash

	# Required for some features
	# Set temp var for load later
	Owner = 0
	OwnerName = ""
	OwnerUsername = ""
	BotID = 0
	BotName = ""
	BotUsername = ""
	# From config
	Command = Config.Command
	NANA_WORKER = Config.NANA_WORKER
	ASSISTANT_WORKER = Config.ASSISTANT_WORKER

	try:
		TEST_DEVELOP = Config.TEST_DEVELOP
		if TEST_DEVELOP:
			BOT_SESSION = Config.BOT_SESSION
			APP_SESSION = Config.APP_SESSION
			log.info("Testing mode activated!")
		else:
			raise AttributeError
	except AttributeError:
		BOT_SESSION = "nana/session/ManageBot"
		APP_SESSION = "nana/session/Nana"

	# APIs
	thumbnail_API = Config.thumbnail_API
	screenshotlayer_API = Config.screenshotlayer_API

	# LOADER
	USERBOT_LOAD = Config.USERBOT_LOAD
	USERBOT_NOLOAD = Config.USERBOT_NOLOAD
	ASSISTANT_LOAD = Config.ASSISTANT_LOAD
	ASSISTANT_NOLOAD = Config.ASSISTANT_NOLOAD

	DB_URL = Config.DB_URL
	ASSISTANT_BOT = Config.ASSISTANT_BOT
	ASSISTANT_BOT_TOKEN = Config.ASSISTANT_BOT_TOKEN
	AdminSettings = Config.AdminSettings
	REMINDER_UPDATE = Config.REMINDER_UPDATE
	TEST_MODE = Config.TEST_MODE

gauth = GoogleAuth()

DB_AVAIABLE = False
BOTINLINE_AVAIABLE = False

# Postgresql
def mulaisql() -> scoped_session:
	global DB_AVAIABLE
	engine = create_engine(DB_URL, client_encoding="utf8")
	BASE.metadata.bind = engine
	try:
		BASE.metadata.create_all(engine)
	except exc.OperationalError:
		DB_AVAIABLE = False
		return False
	DB_AVAIABLE = True
	return scoped_session(sessionmaker(bind=engine, autoflush=False))

async def get_bot_inline(bot):
	global BOTINLINE_AVAIABLE
	if setbot:
		try:
			await app.get_inline_bot_results("@{}".format(bot.username), "test")
			BOTINLINE_AVAIABLE = True
		except errors.exceptions.bad_request_400.BotInlineDisabled:
			BOTINLINE_AVAIABLE = False

async def get_self():
	global Owner, OwnerName, OwnerUsername, AdminSettings
	getself = await app.get_me()
	Owner = getself.id
	if getself.last_name:
		OwnerName = getself.first_name + " " + getself.last_name
	else:
		OwnerName = getself.first_name
	OwnerUsername = getself.username
	if Owner not in AdminSettings:
		AdminSettings.append(Owner)

async def get_bot():
	global BotID, BotName, BotUsername
	getbot = await setbot.get_me()
	BotID = getbot.id
	BotName = getbot.first_name
	BotUsername = getbot.username

BASE = declarative_base()
SESSION = mulaisql()

if ASSISTANT_BOT:
	setbot = Client(BOT_SESSION, api_id=api_id, api_hash=api_hash, bot_token=ASSISTANT_BOT_TOKEN, workers=ASSISTANT_WORKER, test_mode=TEST_MODE)
else:
	setbot = None

app = Client(APP_SESSION, api_id=api_id, api_hash=api_hash, app_version=app_version, device_model=device_model, system_version=system_version, lang_code=lang_code, workers=NANA_WORKER, test_mode=TEST_MODE)
