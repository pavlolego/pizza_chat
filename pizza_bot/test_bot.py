
import unittest
from unittest.mock import MagicMock as M, call, patch
from pizza_bot.bot import PizzaBot
import contextlib

class PizzaBotTestCase(unittest.TestCase):
    """
    PizzaBot instrumentation functionality tests
    """
    '''
    PizzaBot.on_chat_start:
        it invokes start_dialog and run_dialog called
    PizzaBot.on_chat_input:
        it validates dialog against registry
        it invokes run_dialog
    PizzaBot.on_chat_exit:
        it validates dialog against registry
        it invokes delete_dialog
    PizzaBot.start_dialog:
        it resets dialog input
        it adds dialog and its order and machine to registry
    PizzaBot.delete_dialog:
        it removes dialog from registry
    PizzaBot.send_variants:
        it sends message with action variants
    PizzaBot.get_value:
        it returns None for empty input
        it returns invalid object when input is not expected
        it returns variant mapping when input is valid
    PizzaBot.log:
        it prints a message
    '''
    def setUp(self):
        self.bot_manager = M()
        self.dialog = M()
        self.bot = PizzaBot(self.bot_manager)

    def test_manager_is_saved(self):
        assert self.bot.manager is self.bot_manager

    def test_on_chat_start(self):
        mock = M()
        self.bot.start_dialog = mock.start_dialog
        self.bot.run_dialog = mock.run_dialog

        self.bot.on_chat_start(self.dialog)

        assert mock.method_calls == [
            call.start_dialog(self.dialog),
            call.run_dialog(self.dialog),
        ]

    def test_on_chat_input(self):
        self.bot.log = log = M()
        self.bot.run_dialog = run_dialog = M()

        # Run fail
        self.bot.on_chat_input(self.dialog)

        # Assert
        assert log.call_args_list == [
            call('Input received from wrong dialog: {}'.format(self.dialog))
        ]
        assert run_dialog.call_count == 0

        # Reset
        log.reset_mock(), run_dialog.reset_mock()
        self.bot.dialogs[self.dialog] = M(), M()

        # Run successful
        self.bot.on_chat_input(self.dialog)

        # Assert
        assert log.call_count == 0
        assert run_dialog.call_args_list == [
            call(self.dialog)
        ]

    def test_on_chat_exit(self):
        self.bot.log = log = M()
        self.bot.delete_dialog = delete_dialog = M()

        # Run fail
        self.bot.on_chat_exit(self.dialog)

        # Assert
        assert log.call_args_list == [
            call('Exit received from wrong dialog: {}'.format(self.dialog))
        ]
        assert delete_dialog.call_count == 0

        # Reset
        log.reset_mock(), delete_dialog.reset_mock()
        self.bot.dialogs[self.dialog] = M(), M()

        # Run successful
        self.bot.on_chat_exit(self.dialog)

        # Assert
        assert log.call_count == 0
        assert delete_dialog.call_args_list == [
            call(self.dialog)
        ]

    def test_start_dialog(self):
        with patch('pizza_bot.bot.Machine') as Machine,\
            patch('pizza_bot.bot.Order') as Order:
            self.bot.start_dialog(self.dialog)

        assert self.dialog in self.bot.dialogs
        order, machine = self.bot.dialogs[self.dialog]
        assert order == Order.return_value
        assert machine == Machine.return_value
        assert Order.call_args_list == [
            call()
        ]
        assert Machine.call_args_list == [
            call(
                model=order,
                states=PizzaBot.states,
                transitions=PizzaBot.transitions,
                initial='idle'
            )
        ]

    def test_delete_dialog(self):
        it = M()
        self.bot.dialogs[it] = it
        self.bot.delete_dialog(it)
        assert it not in self.bot.dialogs

    def test_send_variants(self):
        self.bot.variants = {'s': {'k': 'l', 'm': 'n'}, 'p': {'a':'b', 'c':'d'}}
        order, machine = M(), M()
        order.state = 's'
        self.bot.messages = {'please_repeat': 'hhh{variants}ooo'}
        self.bot.dialogs[self.dialog] = order, machine

        self.bot.send_variants(self.dialog)

        assert self.dialog.send_message.call_args_list == [
            call('hhhk, mooo')
        ]

    def test_get_value(self):
        pass

    def test_log(self):
        pass


class PizzaBotDialogTestCase(unittest.TestCase):
    """
    PizzaBot conversation tests
    """
    pass


class InterfaceTestCase(unittest.TestCase):
    """
    Test interface implementation match to certain rules
    """
    pass
