
import unittest
from unittest.mock import MagicMock as M, call, patch
from pizza_bot.bot import PizzaBot
import contextlib

'''
bot / PizzaBot
'''


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
    PizzaBot.run_dialog:
        it calls correct handlers
        it passing proper arguments
    PizzaBot.handle_idle:
        it prompts
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

        with self.subTest('Test on_chat_input fails'):
            self.bot.on_chat_input(self.dialog)

            # Assert
            assert log.call_args_list == [
                call('Input received from wrong dialog: {}'.format(self.dialog))
            ]
            assert run_dialog.call_count == 0

        # Reset
        log.reset_mock(), run_dialog.reset_mock()
        self.bot.dialogs[self.dialog] = M(), M()

        with self.subTest('Test on_chat_input passes'):
            self.bot.on_chat_input(self.dialog)

            # Assert
            assert log.call_count == 0
            assert run_dialog.call_args_list == [
                call(self.dialog)
            ]

    def test_on_chat_exit(self):
        self.bot.log = log = M()
        self.bot.delete_dialog = delete_dialog = M()

        with self.subTest('Test on_chat_exit fails'):
            self.bot.on_chat_exit(self.dialog)

            # Assert
            assert log.call_args_list == [
                call('Exit received from wrong dialog: {}'.format(self.dialog))
            ]
            assert delete_dialog.call_count == 0

        # Reset
        log.reset_mock(), delete_dialog.reset_mock()
        self.bot.dialogs[self.dialog] = M(), M()

        with self.subTest('Test on_chat_exit passes'):
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

    def test_run_dialog(self):
        """Test run_dialog properly handle order states"""

        states = 'idle', 'size_picked', 'payment_picked'
        handler_names = 'handle_idle', 'handle_size_pick', 'handle_payment_pick'

        matrix = [
            (1, 0, 0),
            (1, 1, 0),
            (1, 1, 1),
        ]
        self.bot.get_value = M()
        self.bot.start_dialog(self.dialog)
        order, machine = self.bot.dialogs[self.dialog]

        # Patch handlers
        mocks = []
        for handler_name in handler_names:
            m = M()
            mocks.append(m)
            setattr(self.bot, handler_name, m)

        # Do Checks for each of them
        for method, state, calls in zip(mocks, states, matrix):
            self.bot.get_value.return_value = value = object()
            order.state = state
            self.bot.run_dialog(self.dialog)
            self.assertEqual(method.call_args_list, [call(self.dialog, order, value)])
            self.assertEqual(calls, tuple(m.call_count for m in mocks))

    def test_handle_idle(self):
        order = M()
        self.bot.send_variants = send_variants = M()
        dialog = self.dialog
        positive_input = 12345
        mocks = dialog.send_message, send_variants, order.set_size
        ignore = object()
        pick_size_call = call(self.bot.messages.get('pick_size'))
        pick_payment_call = call(self.bot.messages.get('pick_payment'))
        asserts = {
            # dialog.send_message, send_variants, order.set_size
            None: [ [pick_size_call], [], [] ],
            self.bot.INVALID: [ [pick_size_call], [call(self.dialog)], [] ],
            positive_input: [ [pick_payment_call], [], [call.set_size(positive_input)] ],
        }

        for chat_input, expected in asserts.items():
            for mock in mocks:
                mock.reset_mock()
            with self.subTest('Test handle_idle against {}'.format(chat_input)):
                self.bot.handle_idle(dialog, order, chat_input)
                for mock, value in zip(mocks, expected):
                    self.assertEqual(mock.call_args_list, value)

    def test_handle_size_pick(self):
        '''
        invalid - send_message, send_variants
        valid - set_payment, send_message
        '''
        dialog = self.dialog
        positive_input = 3463
        self.bot.send_variants = send_variants = M()
        order = M()
        order.size_description = 'kkkk'
        order.payment_description = 'fffffff'
        args = dict(pizza_size=order.size_description, payment_type=order.payment_description)
        mocks = dialog.send_message, send_variants, order.set_payment
        asserts = {
            self.bot.INVALID: [
                [call(self.bot.messages.get('pick_payment'))],
                [call(dialog)],
                []
            ],
            positive_input: [
                [call(self.bot.messages.get('confirm_pick').format(**args))],
                [],
                [call(positive_input)]
            ],
        }
        for chat_input, expected in asserts.items():
            for mock in mocks:
                mock.reset_mock()
            with self.subTest('Test handle_size_pick against {}'.format(chat_input)):
                self.bot.handle_size_pick(dialog, order, chat_input)
                for mock, value in zip(mocks, expected):
                    self.assertEqual(mock.call_args_list, value)

    def test_handle_payment_pick(self):
        '''
        invalid - send_message,send_variants
        valid - confirm, start_dialog, send_message
        valid(is_confirmed) - confirm, send_message, create_order, start_dialog, send_message
        '''
        dialog = self.dialog
        positive_input = 3463
        positive_input_2 = 5683
        self.bot.send_variants = send_variants = M()
        self.bot.start_dialog = start_dialog = M()
        order = M()
        order.size_description = 'afks'
        order.payment_description = 'fjdrt5'
        args = dict(pizza_size=order.size_description, payment_type=order.payment_description)
        mocks = dialog.send_message, send_variants, order.confirm,\
                self.bot_manager.create_order, start_dialog
        # TODO: Complete test case
        asserts = {
            self.bot.INVALID: [
                [call(self.bot.messages.get('confirm_pick').format(**args))],
                [call(dialog)],
                [],
                [],
                [],
            ],
            positive_input: [
                [call(self.bot.messages.get('pick_size'))],
                [],
                [call(positive_input)],
                [],
                [call(dialog)],
            ],
            positive_input_2: [
                [
                    call(self.bot.messages.get('success')),
                    call(self.bot.messages.get('pick_size'))
                ],
                [],
                [call(positive_input_2)],
                [call(dialog, order)],
                [call(dialog)],
            ],
        }
        for chat_input, expected in asserts.items():
            for mock in mocks:
                mock.reset_mock()
            with self.subTest('Test handle_payment_pick against {}'.format(chat_input)):
                order.is_confirmed = chat_input == positive_input_2
                self.bot.handle_payment_pick(dialog, order, chat_input)
                for mock, value in zip(mocks, expected):
                    self.assertEqual(mock.call_args_list, value)

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
        self.bot.variants = {
            'state_1': {
                'kkz': 'l',
                'mfp': 'n'
            },
            'state_2': {
                'aek': 'b',
                'chv': 'd'
            }
        }
        dialog = self.dialog
        order = M()
        order.state = 'state_1'
        self.bot.dialogs[dialog] = order, M()

        '''
        None input - returns None
        Invalid(at all) input - returns INVALID
        Invalid(depending on state) input - returns INVALID
        Valid input - returns matching variant
        Valid(wrong case) input - returns matching variant
        '''
        asserts = {
            None: None,
            'dfkFFhk': self.bot.INVALID,
            'aek': self.bot.INVALID,
            'kkz': 'l',
            'MFP': 'n',
        }
        for inp, out in asserts.items():
            with self.subTest('Test get_value for input {}'.format(inp)):
                dialog.get_input.return_value = inp
                rv = self.bot.get_value(dialog)
                self.assertEqual(order.state, 'state_1')
                self.assertEqual(out, rv)

    def test_log(self):
        message = 'TTTTtest'
        with patch('pizza_bot.bot.logging.info') as cm:
            self.bot.log(message)

        self.assertEqual(cm.call_args_list, [
            call(message)
        ])
