import sys
import traceback
from uuid import uuid4
from nana import app, setbot, Owner, OwnerName
from nana.helpers.string import parse_button, build_keyboard

from pyrogram import errors, Filters, InlineKeyboardMarkup, InputTextMessageContent, InlineKeyboardButton
from pyrogram import InlineQueryResultArticle
from nana.helpers.msg_types import Types
from nana.modules.database import notes_db

# TODO: Add more inline query
# TODO: Wait for pyro update to add more inline query
GET_FORMAT = {
	Types.TEXT.value: InlineQueryResultArticle,
	# Types.DOCUMENT.value: InlineQueryResultDocument,
	# Types.PHOTO.value: InlineQueryResultPhoto,
	# Types.VIDEO.value: InlineQueryResultVideo,
	# Types.STICKER.value: InlineQueryResultCachedSticker,
	# Types.AUDIO.value: InlineQueryResultAudio,
	# Types.VOICE.value: InlineQueryResultVoice,
	# Types.VIDEO_NOTE.value: app.send_video_note,
	# Types.ANIMATION.value: InlineQueryResultGif,
	# Types.ANIMATED_STICKER.value: InlineQueryResultCachedSticker,
	# Types.CONTACT: InlineQueryResultContact
}

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
			switch_pm_parameter="help_inline"
		)
		return

	if string.split()[0] == "#note":
		if len(string.split()) == 1:
			allnotes = notes_db.get_all_selfnotes_inline(query.from_user.id)
			if not allnotes:
				await client.answer_inline_query(query.id,
					results=answers,
					switch_pm_text="You dont have any notes!",
					switch_pm_parameter="help_inline"
				)
				return
			if len(list(allnotes)) >= 30:
				rng = 30
			else:
				rng = len(list(allnotes))
			for x in range(rng):
				note = allnotes[list(allnotes)[x]]
				noteval = note["value"]
				notetype = note["type"]
				# notefile = note["file"]
				if notetype != Types.TEXT:
					continue
				note, button = parse_button(noteval)
				button = build_keyboard(button)
				answers.append(InlineQueryResultArticle(
						id=uuid4(),
						title="Note #{}".format(list(allnotes)[x]),
						description=note,
						input_message_content=InputTextMessageContent(note),
						reply_markup=InlineKeyboardMarkup(button)))
			await client.answer_inline_query(query.id,
				results=answers,
				switch_pm_text="Yourself notes",
				switch_pm_parameter="help_inline"
			)
			return
		q = string.split(None, 1)
		notetag = q[1]
		noteval = notes_db.get_selfnote(query.from_user.id, notetag)
		if not noteval:
			await client.answer_inline_query(query.id,
				results=answers,
				switch_pm_text="Note not found!",
				switch_pm_parameter="help_inline"
			)
			return
		note, button = parse_button(noteval.get('value'))
		button = build_keyboard(button)
		answers.append(InlineQueryResultArticle(
						id=uuid4(),
						title="Note #{}".format(notetag),
						description=note,
						input_message_content=InputTextMessageContent(note),
						reply_markup=InlineKeyboardMarkup(button)))
		try:
			await client.answer_inline_query(query.id,
				results=answers,
				cache_time=5,
			)
		except errors.exceptions.bad_request_400.MessageEmpty:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			log_errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
			button = InlineKeyboardMarkup([[InlineKeyboardButton("🐞 Report bugs", callback_data="report_errors")]])
			text = "An error has accured!\n\n```{}```\n".format("".join(log_errors))
			await setbot.send_message(Owner, text, reply_markup=button)
			return

	await client.answer_inline_query(query.id,
		results=answers,
		switch_pm_text="Need help? Click here",
		switch_pm_parameter="help_inline"
	)
