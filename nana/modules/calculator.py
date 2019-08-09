import sys
import traceback
from currency_converter import CurrencyConverter

from nana import app, Command, logging
from pyrogram import Filters

__MODULE__ = "Calculator"
__HELP__ = """
Calculator, converting, math, etc.

──「 **Evaluation** 」──
-> `eval (command)`
Example: `eval 1+1`
Math can be used: `+, -, *, /`

──「 **Money converting** 」──
-> `curr (command)`

"""

c = CurrencyConverter()

@app.on_message(Filters.user("self") & Filters.command(["eval"], Command))
async def evaluation(client, message):
	if len(message.text.split()) == 1:
		await message.edit("Usage: `eval 1000-7`")
		return
	q = message.text.split(None, 1)[1]
	try:
		ev = str(eval(q))
		if ev:
			if len(ev) >= 4096:
				file = open("nana/cache/output.txt", "w+")
				file.write(ev)
				file.close()
				await client.send_file(message.chat.id, "nana/cache/output.txt", caption="`Output too large, sending as file`")
				os.remove("nana/cache/output.txt")
				return
			else:
				await message.edit("**Query:**\n{}\n\n**Result:**\n`{}`".format(q, ev))
				return
		else:
			await message.edit("**Query:**\n{}\n\n**Result:**\n`None`".format(q))
			return
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
		await message.edit("Error: `{}`".format(code, "".join(errors)))
		logging.exception("Evaluation error")


@app.on_message(Filters.user("self") & Filters.command(["curr"], Command))
async def evaluation(client, message):
	if len(message.text.split()) <= 3:
		await message.edit("Usage: `curr 100 USD IDR`")
		return
	value = message.text.split(None, 3)[1]
	curr1 = message.text.split(None, 3)[2].upper()
	curr2 = message.text.split(None, 3)[3].upper()
	try:
		conv = c.convert(int(value), curr1, curr2)
		text = "{} {} = {} {}".format(curr1, value, curr2, f'{conv:,.2f}')
		await message.edit(text)
	except ValueError as err:
		await message.edit(str(err))
