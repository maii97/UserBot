import re
from html import escape

from nana import app, Command, lang_code
from pyrogram import Filters

__MODULE__ = "Stylish Text"
__HELP__ = """
Convert your text to stylish text!

Use this custom format:
-> `<upside>Upside-down text</upside>` = `ʇxəʇ uʍop-əp!sp∩`
-> `<oline>Overline text</oline>` = `O̅v̅e̅r̅l̅i̅n̅e̅ ̅t̅e̅x̅t̅`
-> `<strike>Strike text</strike>` = `S̶t̶r̶i̶k̶e̶ ̶t̶e̶x̶t̶`
-> `<unline>Underline text</unline>` = `U̲n̲d̲e̲r̲l̲i̲n̲e̲ ̲t̲e̲x̲t̲`

──「 **Stylish Generator** 」──
-> `stylish Your text here <upside>with</upside> <strike>formatted</strike> <unline>style</unline>`
Stylish your text easily, can be used as caption and text.

Example:
Input = `stylish Your text here <upside>with</upside> <strike>formatted</strike> <unline>style</unline>`
Output = `Your text here ɥʇ!ʍ f̶o̶r̶m̶a̶t̶t̶e̶d̶ s̲t̲y̲l̲e̲`
"""

upsidedown_dict = {
	'a':'ɐ', 'b':'q', 'c':'ɔ', 'd':'p', 'e':'ə',
	'f':'ɟ', 'g':'ɓ', 'h':'ɥ', 'i':'!', 'j':'ɾ',
	'k':'ʞ', 'l':'l', 'm':'ɯ', 'n':'u', 'o':'o',
	'p':'p', 'q':'q', 'r':'ɹ', 's':'s', 't':'ʇ',
	'u':'n', 'v':'ʌ', 'w':'ʍ', 'x':'x', 'y':'ʎ',
	'z':'z',
	'A':'∀', 'B':'B', 'C':'Ↄ', 'D':'◖', 'E':'Ǝ',
	'F':'Ⅎ', 'G':'⅁', 'H':'H', 'I':'I', 'J':'ſ',
	'K':'K', 'L':'⅂', 'M':'W', 'N':'ᴎ', 'O':'O',
	'P':'Ԁ', 'Q':'Ό', 'R':'ᴚ', 'S':'S', 'T':'⊥',
	'U':'∩', 'V':'ᴧ', 'W':'M', 'X':'X', 'Y':'⅄',
	'Z':'Z',
	'0':'0', '1':'1', '2':'0', '3':'Ɛ', '4':'ᔭ',
	'5':'5', '6':'9', '7':'Ɫ', '8':'8', '9':'0',
	'_':'¯', "'":',', ',':"'", '\\':'/', '/':'\\',
	'!':'¡', '?':'¿',
}
CHAR_OVER = chr(0x0305)
CHAR_UNDER = chr(0x0332)
CHAR_STRIKE = chr(0x0336)

def text_style_generator(text, text_type):
	teks = list(text)
	for i, ele in enumerate(teks):
		teks[i] = teks[i] + text_type
	pesan = ""
	for x in range(len(teks)):
		pesan += teks[x]
	return pesan

@app.on_message(Filters.user("self") & Filters.command(["stylish"], Command))
async def stylish_generator(client, message):
	if message.text and len(message.text.split()) == 1 or message.caption and len(message.caption.split()) == 1:
		await message.edit("Usage: `stylish your text goes here`")
		return
	
	if message.caption:
		text = message.caption.split(None, 1)[1]
	else:
		text = message.text.split(None, 1)[1]

	# Converting to upside-down text: upside
	upside_compile = re.compile(r'<upside>(.*?)</upside>')
	src_code = upside_compile.findall(text)
	for x in src_code:
		line = x.strip("\r\n")
		xline = ''.join([upsidedown_dict[c] if c in upsidedown_dict else c for c in line[::-1]])
		text = re.sub(r'<upside>(.*?)</upside>', xline, text, 1)

	# Converting to overlined: oline
	overlined_compile = re.compile(r'<oline>(.*?)</oline>')
	src_code = overlined_compile.findall(text)
	for x in src_code:
		compiled = text_style_generator(x, CHAR_OVER)
		text = re.sub(r'<oline>(.*?)</oline>', compiled, text, 1)
	
	# Converting to understrike: unline
	overlined_compile = re.compile(r'<unline>(.*?)</unline>')
	src_code = overlined_compile.findall(text)
	for x in src_code:
		compiled = text_style_generator(x, CHAR_UNDER)
		text = re.sub(r'<unline>(.*?)</unline>', compiled, text, 1)

	if message.caption:
		await message.edit_caption(text)
	else:
		await message.edit(text)
