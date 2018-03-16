
import unittest
import io
from unittest.mock import MagicMock as M, patch, call
from pizza_bot.console_chat import ConsoleDialog, ConsoleTransactionManager


'''
console_chat / ConsoleDialog
console_chat / ConsoleTransactionManager
'''



class ConsoleDialogTestCase(unittest.TestCase):
    """
    test
    """
    def setUp(self):
        self.bot = M()
        self.maxDiff = None
        self.dialog = ConsoleDialog(self.bot)

    def test_reset_input(self):
        # Test input set to None
        self.dialog.input = object()
        self.dialog.reset_input()
        self.assertIsNone(self.dialog.input)

    def test_get_input(self):
        # Test input return from get_input
        self.dialog.input = inp = object()
        rv = self.dialog.get_input()
        self.assertIs(rv, inp)

    def test_send_message(self):
        # Test passed messages stored in messages field in correct order
        messages = [
            'dhskthslkt',
            'kserhlskrhj',
            'ksmhtklst'
        ]
        self.assertEqual(self.dialog.messages, [])
        for msg in messages:
            self.dialog.send_message(msg)
        self.assertListEqual(self.dialog.messages, messages)

    def test_run_chat(self):
        '''
        fails on on_chat_start with exception logged, and on_chat_exit
        passes with: run_chat_cycle called in loop and on_chat_exit called after
        '''
        # self.fail()
        type_err = TypeError()
        mocker = M()
        self.bot.on_chat_start = mocker.on_chat_start
        self.bot.on_chat_exit = mocker.on_chat_exit
        self.dialog.run_chat_cycle = mocker.run_chat_cycle
        mocker.run_chat_cycle.side_effect = [True, True, False]
        asserts = {
            'fail on on_chat_start': {
                'fails': True,
                'calls': [
                    call.on_chat_start(self.dialog),
                    call.logging.exception(type_err),
                    call.on_chat_exit(self.dialog),
                ]
            },
            'succeeds': {
                'fails': False,
                'calls': [
                    call.on_chat_start(self.dialog),
                    call.run_chat_cycle(),
                    call.run_chat_cycle(),
                    call.run_chat_cycle(),
                    call.on_chat_exit(self.dialog),
                ]
            },
        }
        with patch('pizza_bot.console_chat.logging', new=mocker.logging):
            for title, case in asserts.items():
                mocker.reset_mock()
                with self.subTest('Test run_chat {}'.format(title)):
                    mocker.on_chat_start.side_effect = type_err if case['fails'] else None
                    self.dialog.run_chat()
                    self.assertListEqual(mocker.method_calls, case['calls'])


    def test_run_chat_cycle(self):
        input_value = object()
        mocker = M()

        self.dialog.process_messages = mocker.process_messages
        self.dialog.reinit_chat = mocker.reinit_chat
        self.bot.on_chat_input = mocker.on_chat_input

        mocker.process_messages.return_value = last_message = 'sjstrjstj'
        type_err = TypeError()

        asserts = {
            'fails': {
                'return_value': False,
                'input': False,
                'on_chat_input': False,
                'calls': [
                    call.process_messages(),
                    call.input('{}:\n'.format(last_message)),
                ],
            },
            'succeeds with chat reinit': {
                'return_value': True,
                'input': True,
                'on_chat_input': True,
                'calls': [
                    call.process_messages(),
                    call.input('{}:\n'.format(last_message)),
                    call.on_chat_input(self.dialog),
                    call.logging.exception(type_err),
                    call.reinit_chat(),
                ],
            },
            'succeeds': {
                'return_value': True,
                'input': True,
                'on_chat_input': False,
                'calls': [
                    call.process_messages(),
                    call.input('{}:\n'.format(last_message)),
                    call.on_chat_input(self.dialog),
                ],
            },
        }
        with patch('pizza_bot.console_chat.logging', new=mocker.logging),\
                patch('builtins.input', new=mocker.input):
            for title, case in asserts.items():
                mocker.reset_mock()
                with self.subTest('Test run_chat_cycle {}'.format(title)):
                    mocker.on_chat_input.side_effect = type_err if case['on_chat_input'] else None
                    mocker.input.return_value = input_value if case['input'] else None
                    mocker.input.side_effect = None if case['input'] else KeyboardInterrupt
                    with patch('builtins.input', new=mocker.input):
                        rv = self.dialog.run_chat_cycle()
                    self.assertListEqual(mocker.method_calls, case['calls'])
                    self.assertEqual(case['return_value'], rv)

    def test_process_messages(self):
        mocker = M()
        self.dialog.reinit_chat = mocker.reinit_chat
        messages = 'abc def ghi'.split()
        last_message = messages[-1]
        output = '\n{}\n'.format('\n'.join(messages[:-1]))
        asserts = {
            'process_messages with reinit': {
                'no_messages': True,
                'calls': [
                    call.logging.error('No messages for sending!!!'),
                    call.reinit_chat(),
                ]
            },
            'regular process_messages': {
                'no_messages': False,
                'calls': []
            }
        }
        extend = lambda: self.dialog.messages.extend(messages)
        with patch('pizza_bot.console_chat.logging', new=mocker.logging):
            for title, case in asserts.items():
                mocker.reset_mock()
                self.dialog.messages = []
                if case['no_messages']:
                    mocker.reinit_chat.side_effect = extend
                else:
                    extend()
                with self.subTest('Test {} call'.format(title)),\
                        patch('sys.stdout', new_callable=io.StringIO) as cm:
                    rv = self.dialog.process_messages()
                    self.assertEqual(rv, messages[-1])
                    self.assertListEqual(mocker.method_calls, case['calls'])
                    self.assertListEqual(self.dialog.messages, [])
                    self.assertEqual(cm.getvalue(), output)

    def test_reinit_chat(self):
        self.dialog.reinit_chat()
        self.assertListEqual(self.bot.method_calls, [
            call.on_chat_exit(self.dialog),
            call.on_chat_start(self.dialog),
        ])


class ConsoleTransactionManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = ConsoleTransactionManager()

    def test_create_order(self):
        dialog = M()
        order = M()
        order.pizza_size = 'hsdfh'
        order.payment_method = 'fdgjjfg'
        order.is_confirmed = 'serhs'
        expected_output = (
            'Order created:\n'
            '\tPizza size: {}\n'
            '\tPayment type: {}\n'
            '\tOrder confirmed: {}\n'
            '\n'
        ).format(order.pizza_size, order.payment_method, order.is_confirmed)
        with patch('sys.stdout', new_callable=io.StringIO) as cm:
            self.manager.create_order(dialog, order)
        output = cm.getvalue()
        self.assertEqual(output, expected_output)
