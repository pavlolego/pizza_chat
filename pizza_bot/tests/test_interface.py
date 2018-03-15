
import unittest
from pizza_bot.interface import Dialog, Order

class DialogTestCase(unittest.TestCase):
    def test_interface(self):
        """
        Assert base interface contracts are preserved
        """
        dialog = Dialog()
        required_methods = 'reset_input', 'get_input', 'send_message'
        for method in required_methods:
            self.assertTrue(hasattr(dialog, method))
            args = ('Message',) if method == 'send_message' else ()
            self.assertRaises(NotImplementedError, getattr(dialog, method), *args)


class OrderTestCase(unittest.TestCase):
    """
    Test Order object
    """

    def test_size_description(self):
        matches = {
            Order.SMALL_SIZE: 'маленькую',
            Order.BIG_SIZE: 'большую'
        }
        with self.subTest('Test correct values'):
            for value, expected in matches.items():
                order = Order()
                order.pizza_size = value
                self.assertEqual(order.size_description, expected)

        with self.subTest('Test invalid value'):
            order = Order()
            order.pizza_size = object()
            expected = ('Wrong pizza size specified {!r}'.format(order.pizza_size),)
            with self.assertRaises(TypeError) as cm:
                 order.size_description
            self.assertEqual(cm.exception.args, expected)

    def test_payment_description(self):
        matches = {
            Order.PAY_CHECK: 'наличкой',
            Order.PAY_CARD: 'картой'
        }
        with self.subTest('Test correct values'):
            for value, expected in matches.items():
                order = Order()
                order.payment_method = value
                self.assertEqual(order.payment_description, expected)

        with self.subTest('Test invalid value'):
            order = Order()
            order.payment_method = object()
            expected = ('Wrong payment type specified {!r}'.format(order.payment_method),)
            with self.assertRaises(TypeError) as cm:
                 order.payment_description
            self.assertEqual(cm.exception.args, expected)

    def test_setters(self):
        setters = 'set_pizza_size', 'set_payment_method', 'set_confirmation'
        target_fields = 'pizza_size', 'payment_method', 'is_confirmed'
        value = object()

        for setter, target_field in zip(setters, target_fields):
            with self.subTest('Test setter {}'.format(setter)):
                order = Order()
                self.assertEqual(getattr(order, target_field), None)
                setter_callable = getattr(order, setter)
                setter_callable(value)
                self.assertEqual(getattr(order, target_field), value)
