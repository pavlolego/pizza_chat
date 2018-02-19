#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Bot to reply to Telegram messages.
This is built on the API wrapper, see echobot2.py to see the same example built
on the telegram.ext bot framework.
This program is dedicated to the public domain under the CC0 license.
"""
import os
import logging
import time
from functools import partial

import telegram
import telegram.ext
from telegram.utils.request import Request
from pizza_bot.telegram_chat import TelegramDialog
from pizza_bot.console_chat import ConsoleTransactionManager
from pizza_bot.bot import PizzaBot


def gc_callback(bot: telegram.Bot, job: telegram.ext.Job):
    """Purge old dialogs"""
    logging.debug('Purging old dialogs')
    timestamp = time.time() - job.context['threshold']
    dispatcher = job.context['dispatcher']
    for chat_data in dispatcher.chat_data.values():
        dialog = chat_data.get('dialog', None)
        if dialog is None or dialog.last_received is None or dialog.last_received >= timestamp:
            continue
        logging.debug('Purging dialog {}'.format(dialog))
        del chat_data['dialog']


def message_handler(pizza_bot: PizzaBot, bot: telegram.Bot, update: telegram.Update, chat_data: dict):
    """Handle incoming messages"""
    logging.debug('Update processing {}'.format(update))
    is_chat_start = False
    if 'dialog' not in chat_data:
        chat_data['dialog'] = TelegramDialog(bot)
        is_chat_start = True

    dialog = chat_data['dialog']
    dialog.process_update(update)

    if is_chat_start:
        pizza_bot.on_chat_start(dialog)
    pizza_bot.on_chat_input(dialog)


def main():
    """Run the bot."""

    # Url to access bot: https://t.me/pizza_3468_bot

    # Settings used by bot:
    # Bot token
    token = '453704416:AAEhuUw0XiMa4QM7u8OLaNTqvO65Fs9djUk'
    # gc_callback job settings
    threshold = 30 * 60  # 30min in seconds, threshold for last message in chat
    interval = 5 * 60 # 5min in seconds, checks interval


    # Set logging format
    log_level = os.environ.get('LOGLEVEL', None)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=log_level and int(log_level))
    if log_level is not None:
        logging.getLogger('telegram.utils.webhookhandler').setLevel(int(log_level))

    # Telegram Bot Authorization Token
    cpus = os.cpu_count()
    request = Request(con_pool_size=cpus+4)
    bot = telegram.Bot(token, request=request)
    updater = telegram.ext.Updater(bot=bot, workers=cpus)

    # Add repeating job to get rid of old chats
    context = dict(threshold=threshold, dispatcher=updater.dispatcher)
    job = updater.job_queue.run_repeating(callback=gc_callback, interval=interval, context=context)

    # Create pizza bot machine
    manager = ConsoleTransactionManager()
    pizza_bot = PizzaBot(manager)

    # Add handler to process updates aka incoming messages
    handler = telegram.ext.MessageHandler(
        filters=telegram.ext.Filters.all,
        callback=partial(message_handler, pizza_bot),
        pass_chat_data=True)
    updater.dispatcher.add_handler(handler)

    port = int(os.environ.get('PORT', '8443'))
    updater.start_webhook(listen='0.0.0.0', port=port, url_path=token)
    updater.bot.set_webhook('https://pizza-bot-3468.herokuapp.com/'+token)
    updater.idle()


if __name__ == '__main__':
    main()
