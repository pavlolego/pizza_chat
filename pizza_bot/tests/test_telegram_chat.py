
import unittest
from unittest.mock import MagicMock as M, patch, call
from pizza_bot.telegram_chat import TelegramDialog


class TelegramDialogTestCase(unittest.TestCase):
    """
    Telegram dialog implementation implement the interface and do proper processing.

    test_reset_input:
        It drops message
        It affects get_input result

    test_get_input:
        It returns expected input
        It returns same input between calls

    test_send_message:
        It raise exception for empty chat
        It deliver message to bot

    test_process_update:
        It raises exception for empty message
        It initialize and validate(raises exception) a chat reference
        It saves a message
        It records message timestamp

    test_magic_str:
        It renders expected string
    """
    def setUp(self):
        self.bot = M()
        self.dialog = TelegramDialog(self.bot)

    def test_reset_input(self):
        self.dialog.message = object()
        self.dialog.reset_input()
        self.assertIsNone(self.dialog.message)

    def test_get_input(self):
        self.dialog.message = message = object()
        rv = self.dialog.get_input()
        self.assertIs(rv, message)

    def test_send_message(self):
        message = object()
        with self.subTest('Test send_message raises exception'):
            self.dialog.chat = None
            with self.assertRaises(TypeError) as cm:
                self.dialog.send_message(message)
            self.assertEqual(cm.exception.args, ('No chat to send a message',))

        with self.subTest('Test send_message passes message to bot'):
            self.dialog.chat = chat = object()
            self.dialog.send_message(message)
            self.assertListEqual(self.bot.method_calls, [
                call.send_message(chat, message)
            ])

    def test_process_update(self):
        '''
        - fails on None message
        - fails when chat not match to arrived message
        - succeeds, assigns a chat, message and last_received time
        '''
        mocker = M()
        update = mocker.update
        chat = object()
        message = object()
        mocker.time.return_value = time_value = object()
        time_patch = patch('pizza_bot.telegram_chat.time.time', new=mocker.time)
        time_patch.start()
        asserts = {
            'fails on wrong message': {
                'message': None,
                'chat': None,
                'exc': TypeError('Update with empty message')
            },
            'fails on wrong chat': {
                'message': M(text=object(), chat_id=chat),
                'chat': object(),
                'exc': TypeError('Chat integrity error')
            },
            'succeeds with chat assigned': {
                'message': M(text=message, chat_id=chat),
                'chat': None,
                'exc': None
            },
            'succeeds without chat assigned': {
                'message': M(text=message, chat_id=chat),
                'chat': chat,
                'exc': None
            },
        }
        for title, case in asserts.items():
            with self.subTest('Test process_update {}'.format(title)):
                mocker.reset_mock()
                update.message = case['message']
                self.dialog.chat = case['chat']
                self.dialog.message = None
                self.dialog.last_received = None
                if case['exc']:
                    with self.assertRaises(TypeError) as cm:
                        self.dialog.process_update(update)
                    self.assertEqual(cm.exception.args, case['exc'].args)
                else:
                    self.dialog.process_update(update)
                    self.assertEqual(chat, self.dialog.chat)
                    self.assertEqual(message, self.dialog.message)
                    self.assertEqual(time_value, self.dialog.last_received)
                    if case['chat'] is None:
                        self.assertIs(chat, self.dialog.chat)
        time_patch.stop()

    def test_magic_str(self):
        d = self.dialog
        d.last_received = last_received = 'sdfhsreh'
        d.message = message = 'sjrhjlserhl'
        d.chat = chat = 'sthjsrtj'
        expected_string = 'TelegramDialog[last_received={}, message={}, chat={}]'
        self.assertEqual(expected_string.format(last_received, message, chat), str(d))





