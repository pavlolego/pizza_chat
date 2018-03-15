
import logging
from transitions import Machine
from pizza_bot.interface import Dialog, Order, TransactionManager


class PizzaBot(object):
    messages = dict(
        pick_size='Какую вы хотите пиццу? Большую или маленькую?',
        pick_payment='Как вы будете платить?',
        confirm_pick='Вы хотите {pizza_size} пиццу, оплата - {payment_type}?',
        success='Спасибо за заказ!',
        please_repeat='Повторите пожалуста. Варианты: {variants}',
    )

    states = ['idle', 'size_picked', 'payment_picked']
    transitions = [
        dict(trigger='set_size', source='idle', dest='size_picked', before='set_pizza_size'),
        dict(trigger='set_payment', source='size_picked', dest='payment_picked', before='set_payment_method'),
        dict(trigger='confirm', source='payment_picked', dest='idle', before='set_confirmation'),
    ]

    INVALID = object()
    variants = {
        'idle': {'маленькую': Order.SMALL_SIZE, 'большую': Order.BIG_SIZE},
        'size_picked': {'наличкой': Order.PAY_CHECK, 'картой': Order.PAY_CARD},
        'payment_picked': {'да': True, 'нет': False},
    }


    def __init__(self, manager):
        self.manager = manager
        self.dialogs = dict()

    def on_chat_start(self, dialog: Dialog):
        """Notify dialog has started"""
        self.start_dialog(dialog)
        self.run_dialog(dialog)

    def on_chat_input(self, dialog: Dialog):
        """Notify dialog input received"""
        if dialog not in self.dialogs:
            self.log('Input received from wrong dialog: {}'.format(dialog))
            return
        self.run_dialog(dialog)

    def on_chat_exit(self, dialog):
        """Notify dialog is ended"""
        if dialog not in self.dialogs:
            self.log('Exit received from wrong dialog: {}'.format(dialog))
            return
        self.delete_dialog(dialog)

    def start_dialog(self, dialog):
        """Create new dialog"""
        order = Order()
        machine = Machine(
            model=order,
            states=self.states,
            transitions=self.transitions,
            initial='idle'
        )
        self.dialogs[dialog] = (order, machine)
        dialog.reset_input()

    def delete_dialog(self, dialog):
        """Delete dialog"""
        del self.dialogs[dialog]

    def run_dialog(self, dialog):
        order, machine = self.dialogs[dialog]
        chat_input = self.get_value(dialog)

        # Transition handler: idle -> size_picked
        if order.is_idle():
            self.handle_idle(dialog, order, char_input)

        # Transition handler: size_picked -> payment_picked
        elif order.is_size_picked():
            self.handle_size_pick(dialog, order, char_input)

        # Transition handler: payment_picked -> idle
        elif order.is_payment_picked():
            self.handle_payment_pick(dialog, order, char_input)

    def handle_idle(self, dialog, order, char_input):
        # Handle invalid input
        if chat_input is None or chat_input == self.INVALID:
            dialog.send_message(self.messages.get('pick_size'))
            # For initial state is possible to have no input from user
            # In that case it is greeting, no need to show variants
            if chat_input is not None:
                self.send_variants(dialog)
            return

        # Set pizza size, Move transition to size_picked
        order.set_size(chat_input)

        # Ask for next input
        dialog.send_message(self.messages.get('pick_payment'))

    def handle_size_pick(self, dialog, order, char_input):
        # Handle invalid input
        if chat_input is self.INVALID:
            dialog.send_message(self.messages.get('pick_payment'))
            self.send_variants(dialog)
            return

        # Set order payment method, Move transition to payment_picked
        order.set_payment(chat_input)

        # Ask for next input
        args = dict(pizza_size=order.size_description, payment_type=order.payment_description)
        dialog.send_message(self.messages.get('confirm_pick').format(**args))

    def handle_payment_pick(self, dialog, order, char_input):
        # Handle invalid input
        if chat_input is self.INVALID:
            args = dict(pizza_size=order.size_description, payment_type=order.payment_description)
            dialog.send_message(self.messages.get('confirm_pick').format(**args))
            self.send_variants(dialog)
            return

        # Confirm order, Move transition to idle
        order.confirm(chat_input)

        if order.is_confirmed:
            dialog.send_message(self.messages.get('success'))
            self.manager.create_order(dialog, order)
        self.start_dialog(dialog)
        dialog.send_message(self.messages.get('pick_size'))

    def send_variants(self, dialog):
        order, machine = self.dialogs[dialog]
        state = order.state
        variants = ', '.join(self.variants[state].keys())
        message = self.messages.get('please_repeat')
        dialog.send_message(message.format(variants=variants))

    def get_value(self, dialog):
        order, machine = self.dialogs[dialog]
        state = order.state

        chat_input = dialog.get_input()
        if chat_input is None:
            return None

        chat_input = chat_input.lower().strip()
        if chat_input not in self.variants[state]:
            return self.INVALID

        return self.variants[state][chat_input]

    def log(self, message):
        logging.info(message)
