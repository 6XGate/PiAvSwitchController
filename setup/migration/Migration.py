from typing import Union

import sqlite3

from . import Transaction


class Migration:
    def __init__(self):
        """Initializes a new instance of the Migration class."""
        self.connection = None  # type: Union[None|sqlite3.Connection]

    def begin(self, connection: sqlite3.Connection) -> Transaction:
        """
        Begins a transaction.
        :param connection: The connection.
        :return: The transaction.
        """
        self.connection = connection
        return Transaction(connection)

    def up(self) -> None:
        """Executed when bringing the database up-to-date."""
        pass

    def down(self) -> None:
        """Executed when rolling the database down."""
        pass
