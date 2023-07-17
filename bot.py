#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple
from datetime import datetime
from os import getenv

import pytz
from telebot import TeleBot, types


bot = TeleBot(getenv("TGBOTAUTHKEY"))

File = namedtuple('Photo', ['caption', 'filename'])

PHOTOS = [
	File('школьное фото', 'school.png'),
	File('недавнее селфи', 'selfi.jpg'),
]

VOICES = [
	File('Расскажи, пожалуйста, про GPT.', 'gpt.mp3'),
	File('Расскажи, чем NoSQL отличается от SQL.', 'sql.mp3'),
	File(
		'Ты же тоже кожаный мешок, как и мы. Расскажи про любовь-морковь.',
		'love.mp3'
	),
]

REPO_URL = "https://github.com/brawaga/meet-bot-for-yandex"

expect_instructions = False


def make_markup():
	markup = types.ReplyKeyboardMarkup()
	photo_btns = [types.InlineKeyboardButton(photo.caption) for photo in PHOTOS]
	markup.add(*photo_btns)
	return markup


def show_commands(chat_id):
	bot.send_message(
		chat_id,
		"По кнопке ниже можно посмотреть фото, доступна команда /help для "
		"показа доступных действий и /repo для получения ссылки на "
		"репозиторий",
		reply_markup=make_markup()
	)
	bot.send_message(
		chat_id,
		"Я не люблю голосовые сообщения, но меня попросили записать "
		"несколько. Чтобы прослушать, введите кодовую фразу из указанных "
		"ниже. Орфография и пунктуация автора сохранены."
	)
	for voice in VOICES:
		bot.send_message(chat_id, voice.caption)

def process_nextstep(message):
	bot.reply_to(message, 'Инструкция принята.')
	with open('nextstep.txt', 'ta') as f:
		now = datetime.now(tz=pytz.timezone('Europe/Moscow'))
		f.write(
			f'{message.date}\t{now}\t'
			f'{message.from_user.id}\t{message.from_user.username}\t'
			f'{message.text}\n'
		)


def message_handler(*mhargs, **mhkwargs):
	def decorator(fn):
		def replacement(*rargs, **rkwargs):
			global expect_instructions
			if mhkwargs.get('commands', None):
				expect_instructions = False
			elif expect_instructions:
				return process_nextstep(*rargs, **rkwargs)
			return fn(*rargs, **rkwargs)
		return bot.message_handler(*mhargs, **mhkwargs)(replacement)
	return decorator


@message_handler(commands=['start'])
def handle_start(message):
	bot.reply_to(
		message,
		"Привет! Хочешь познакомиться со мной? "
		"Это мой бот-визитка, который поможет тебе в этом."
	)
	show_commands(message.from_user.id)


@message_handler(commands=['help'])
def handle_help(message):
	bot.reply_to(message, 'Напомнить команды? Пожалуйста!')
	show_commands(message.from_user.id)


@message_handler(commands=['repo'])
def handle_help(message):
	bot.reply_to(message, REPO_URL)


@message_handler(commands=['nextstep'])
def handle_nextstep(message):
	global expect_instructions
	if message.text.strip() == '/nextstep':
		bot.reply_to(
			message,
			'Инструкций в команде нет. Следующее ваше сообщение, если оно не '
			'будет командой, будет принято в качестве инструкции.'
		)
		expect_instructions = True
	else:
		process_nextstep(message)


@message_handler(content_types=['text'])
def start(message):
	for photo in PHOTOS:
		if message.text == photo.caption:
			bot.send_message(message.from_user.id, 'вот моё '+photo.caption)
			bot.send_photo(message.from_user.id, photo=open(photo.filename, 'rb'))
			return
	for voice in VOICES:
		if message.text == voice.caption:
			bot.send_audio(message.from_user.id, open(voice.filename, 'rb'))
			return
	bot.reply_to(
		message,
		'Я не волшебник, а только учусь. Вот команды, которые бот понимает:'
	)
	show_commands(message.from_user.id)


bot.infinity_polling()

