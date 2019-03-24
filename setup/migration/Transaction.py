import sqlite3


class Transaction:
    """Provides a scoped SQLite3 transaction."""

    def __init__(self, connection: sqlite3.Connection):
        """
        Initializes a new transaction scoping object.
        :param connection: The connection.
        """
        self.connection = connection

    def __enter__(self) -> None:
        """Required for scoped object, does nothing and returns nothing."""
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commits the transaction."""
        if exc_tb is None:
            self.connection.commit()
        else:
            self.connection.rollback()
