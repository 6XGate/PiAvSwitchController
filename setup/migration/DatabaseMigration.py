import sqlite3

from typing import List, Tuple

from . import Transaction
from . import Migration


# noinspection SqlNoDataSourceInspection,SqlResolve
class DatabaseMigration:
    """Provides a means to execute and rollback database migration code."""

    def __init__(self, database_path: str, migrations: List[Tuple[str, Migration]]):
        """
        Initialization a new instance of the database migration system.
        :param database_path: The path to the database file.
        :param migrations:    The migration code.
        """
        self.connection = sqlite3.connect(database_path)
        self.migrations = migrations

    def migrate(self) -> None:
        """Performs a migration."""
        with Transaction(self.connection):
            self.__create_migration_table()

        batch = 1 + self.__get_latest_batch()

        for date, migration in self.migrations:
            key = "{0}-{1}".format(date, type(migration).__name__)
            if self.__migrated(key):
                continue

            with migration.begin(self.connection):
                migration.up()
                self.__record_migration(key, batch)

            print(key)

    def rollback(self) -> None:
        """Performs a rollback."""
        with Transaction(self.connection):
            self.__create_migration_table()

        batch = self.__get_latest_batch()
        keys = set(self.__get_migrations_in_batch(batch))
        for date, migration in self.migrations:
            key = "{0}-{1}".format(date, type(migration).__name__)
            if key in keys:
                with migration.begin(self.connection):
                    migration.down()
                    self.__record_rollback(key)

    def __record_migration(self, key: str, batch: int) -> None:
        """
        Records the completion of a migration step.
        :param key:   The key to the migration step.
        :param batch: The batch in which the step was executed.
        """
        self.connection.execute("INSERT INTO `migrations`"
                                "    (`name`, `batch`) VALUES"
                                "    (?, ?)", [key, batch])

    def __record_rollback(self, key: str) -> None:
        """
        Records the completion the rollback of a migration step.
        :param key: The key to the migration step.
        """
        self.connection.execute("DELETE FROM `migrations` WHERE"
                                "    `name` = ?", [key])

    def __create_migration_table(self) -> None:
        """Creates the migration table if it does not exist."""
        # Check for the migration table.
        cursor = self.connection.execute("SELECT `name` FROM `sqlite_master` WHERE"
                                         "    `type`='table' AND"
                                         "    `name`='migrations'")
        result = cursor.fetchall()
        if len(result) == 0:
            # Create the migration table.
            self.connection.execute("CREATE TABLE `migrations` ("
                                    "    `name` TEXT(255) UNIQUE,"
                                    "    `batch` INTEGER"
                                    ")")
            self.connection.execute("CREATE INDEX `migrations_batches_index`"
                                    "    ON `migrations` (`batch`)")

    def __get_migrations_in_batch(self, batch: int) -> List[str]:
        """
        Gets all the keys for migrations steps performed in a given batch.
        :param batch: The batch.
        :return: A list of keys for the migration steps.
        """
        cursor = self.connection.execute("SELECT `name` FROM `migrations` WHERE"
                                         "   `batch` = ?", [batch])
        keys = []
        for row in cursor:
            key, *rest = row
            keys.append(key)

        return keys

    def __get_latest_batch(self) -> int:
        """
        Gets the latest batch number.
        :return: The latest batch number.
        """
        cursor = self.connection.execute("SELECT max(`batch`) FROM `migrations` GROUP BY `batch`")
        results = cursor.fetchmany(1)
        if len(results) > 0:
            result, *rest = results
            batch, *rest = result
        else:
            batch = 0

        return batch

    def __migrated(self, key: str) -> bool:
        """
        Determines whether a migration step has been executed.
        :param key: The key to the migration step.
        :return: A value indicating whether the step has been executed.
        """
        cursor = self.connection.execute("SELECT `name` FROM `migrations` WHERE"
                                         "   `name` = ?", [key])
        results = cursor.fetchall()
        return True if len(results) > 0 else False
