
from pizza_bot.interface import Dialog, Order
import telegram
import time

config = {
    'app_id': '77057',
    'api_hash': '2444624a5ea7436cbb1a1865523b0459',
}


class TelegramDialog(Dialog):
    def __init__(self, bot: telegram.Bot):
        super(TelegramDialog, self).__init__()
        self.bot = bot
        self.chat = None
        self.last_received = None
        self.message = None

    def reset_input(self):
        """Reset input before dialog has started"""
        self.message = None

    def get_input(self):
        """Get input received from user"""
        return self.message

    def send_message(self, message):
        """Send message to user"""
        if self.chat is None:
            raise TypeError('No chat to send a message')
        self.bot.send_message(message, chat=self.chat)

    def process_update(self, update: telegram.Update):
        if self.chat is None:
            self.chat = update.effective_chat
        elif self.chat != update.effective_chat:
            raise TypeError('Chat integrity error')

        if update.message is None:
            raise TypeError('Update message is empty')
        self.message = update.message.text
        self.last_received = time.time()

    def __str__(self):
        return 'TelegramDialog[last_received={}, message={}, chat={}]'.format(
            last_received=self.last_received, message=self.message, chat=self.chat)

