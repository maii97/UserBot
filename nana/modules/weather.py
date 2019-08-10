import re
import requests
from html import escape

from nana import app, Command, lang_code
from pyrogram import Filters

__MODULE__ = "Weather"
__HELP__ = """
Take a picture of website. You can select one for use this.

──「 **Take ss website** 」──
-> `print (url)`
Send web screenshot, not full webpage. Send as picture

──「 **Take ss website (more)** 」──
-> `ss (url) (*full)`
Take screenshot of that website, if `full` args given, take full of website and send image as document

* = optional
"""

# TODO: Add more custom args?

@app.on_message(Filters.user("self") & Filters.command(["wttr"], Command))
async def wttr(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `wttr jakarta`")
		return
	location = message.text.split(None, 1)[1]
	h = {'user-agent': 'httpie'}
	a = requests.get(f"https://wttr.in/{location}?mnTC0&lang={lang_code}", headers=h)

	if "Sorry, we processed more than 1M requests today and we ran out of our datasource capacity." in a.text:
		await message.edit("Sorry, location not found!")
		return

	await message.edit(f"<code>{escape(a.text)}</code>", parse_mode='html')
