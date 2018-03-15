

class Dialog(object):
    """
    Interface present given user in certain chat system
    """
    def reset_input(self):
        """Reset input before dialog has started"""
        raise NotImplementedError()

    def get_input(self):
        """Get input received from user"""
        raise NotImplementedError()

    def send_message(self, message):
        """Send message to user"""
        raise NotImplementedError()


class Order(object):
    SMALL_SIZE, BIG_SIZE = range(2)
    PAY_CHECK, PAY_CARD = range(2)

    pizza_size = None
    payment_method = None
    is_confirmed = None

    @property
    def size_description(self):
        if self.pizza_size == self.SMALL_SIZE:
            return 'маленькую'
        elif self.pizza_size == self.BIG_SIZE:
            return 'большую'
        raise TypeError('Wrong pizza size specified {!r}'.format(self.pizza_size))

    @property
    def payment_description(self):
        if self.payment_method == self.PAY_CHECK:
            return 'наличкой'
        elif self.payment_method == self.PAY_CARD:
            return 'картой'
        raise TypeError('Wrong payment type specified {!r}'.format(self.payment_method))

    def set_pizza_size(self, value: int):
        self.pizza_size = value

    def set_payment_method(self, value: int):
        self.payment_method = value

    def set_confirmation(self, value: bool):
        self.is_confirmed = value


class TransactionManager(object):
    def create_order(self, order: Order, dialog: Dialog):
        raise NotImplementedError()
