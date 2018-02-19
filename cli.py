
from pizza_bot.console_chat import ConsoleDialog, ConsoleTransactionManager
from pizza_bot.bot import PizzaBot


def main():
    manager = ConsoleTransactionManager()
    bot = PizzaBot(manager)
    dialog = ConsoleDialog(bot)
    dialog.run_chat()


if __name__ == '__main__':
    main()

