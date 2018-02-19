
import logging
from pizza_bot.interface import Dialog, Order, TransactionManager


class ConsoleDialog(Dialog):
    def __init__(self, bot):
        super(ConsoleDialog, self).__init__()
        self.bot = bot
        self.input = None
        self.messages = []

    def reset_input(self):
        self.input = None

    def get_input(self):
        return self.input

    def send_message(self, message):
        self.messages.append(message)

    def run_chat(self):
        try:
            self.bot.on_chat_start(self)
        except TypeError as e:
            logging.exception(e)
            self.bot.on_chat_exit(self)
            return

        while True:
            # Check messages present
            if not self.messages:
                logging.error('No messages for sending!!!')
                self.reinit_chat()

            # Print messages
            print()
            for message in self.messages[:-1]:
                print(message)
            last_message = self.messages[-1]
            self.messages.clear()

            # Obtain response
            try:
                self.input = input('{}:\n'.format(last_message))
            except KeyboardInterrupt:
                break

            # Process input
            try:
                self.bot.on_chat_input(self)
            except TypeError as e:
                logging.exception(e)
                self.reinit_chat()

        # Done
        self.bot.on_chat_exit(self)

    def reinit_chat(self):
        self.bot.on_chat_exit(self)
        self.bot.on_chat_start(self)


class ConsoleTransactionManager(TransactionManager):
    def create_order(self, dialog: Dialog, order: Order):
        print('Order created:')
        print('\tPizza size: {}'.format(order.pizza_size))
        print('\tPayment type: {}'.format(order.payment_method))
        print('\tOrder confirmed: {}'.format(order.is_confirmed))
        print()

