import sys
import traceback
from uuid import uuid4
from nana import app, setbot, Owner, OwnerName
from nana.helpers.string import parse_button, build_keyboard

from pyrogram import errors, Filters, InlineQueryResultArticle, InlineKeyboardMarkup, InputTextMessageContent
from nana.modules.database import notes_db

# TODO: Add more inline query

@setbot.on_inline_query()
async def inline_query_handler(client, query):
	string = query.query.lower()
	answers = []

	if query.from_user.id != Owner:
		await client.answer_inline_query(query.id,
			results=answers,
			switch_pm_text="Sorry, this bot only for {}".format(OwnerName),
			switch_pm_parameter="createown"
		)
		return

	if string == "":
		await client.answer_inline_query(query.id,
			results=answers,
			switch_pm_text="Need help? Click here",
			switch_pm_parameter="help"
		)
		return

	if string.split()[0] == "#note":
		q = string.split(None, 1)
		notetag = q[1]
		noteval = notes_db.get_selfnote(query.from_user.id, notetag)
		if not noteval:
			await client.answer_inline_query(query.id,
				results=answers,
				switch_pm_text="Note not found!",
				switch_pm_parameter="help"
			)
			return
		note, button = parse_button(noteval.get('value'))
		button = build_keyboard(button)
		answers.append(InlineQueryResultArticle(
						id=uuid4(),
						title="Note #{}".format(notetag),
						input_message_content=InputTextMessageContent(note),
						reply_markup=InlineKeyboardMarkup(button)))
		try:
			await client.answer_inline_query(query.id,
				results=answers,
				cache_time=5,
			)
		except errors.exceptions.bad_request_400.MessageEmpty:
			sys.__excepthook__(errtype, value, tback)
			errors = traceback.format_exception(etype=errtype, value=value, tb=tback)
			button = InlineKeyboardMarkup([[InlineKeyboardButton("🐞 Report bugs", callback_data="report_errors")]])
			text = "An error has accured!\n\n```{}```\n".format("".join(errors))
			if errtype == ModuleNotFoundError:
					text += "\nHint: Try this in your terminal `pip install -r requirements.txt`"
			await setbot.send_message(Owner, text, reply_markup=button)
			return

	await client.answer_inline_query(query.id,
		results=answers,
		switch_pm_text="Need help? Click here",
		switch_pm_parameter="help"
	)
