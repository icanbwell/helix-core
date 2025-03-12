import os
from logging import Logger
from typing import Dict, Any, Optional, List, cast

import pymysql
import sqlparse
from pymysql import OperationalError, MySQLError, Connection
from pymysql.cursors import Cursor
from pymysql.constants import CLIENT

from helixcore.utilities.mysql.pydatabelt.mysql import (
    get_mysql_config,
    construct_mysql_connection_string,
)


class MySqlWriter:
    def __init__(self, *, schema_name: str) -> None:
        """
        This class writes to MySql databases using the pymysql package


        :param schema_name: name of the schema to write to
        """
        assert schema_name, "schema_name should not be None"
        assert isinstance(schema_name, str), "schema_name should be a string"

        env: str = os.getenv("ENV", "local")

        self.db_config: Dict[str, Any] = get_mysql_config(
            "warehouse", env=env, default_schema=schema_name
        )
        self.jdbc_url: str = construct_mysql_connection_string(
            params={"rewriteBatchedStatements": "true"},
            protocol="jdbc:mysql",
            **self.db_config,
        )
        self.username = self.db_config["username"]
        self.password = self.db_config["password"]
        self.host = self.db_config["host"]
        self.port = int(self.db_config["port"])
        self.schema_name: str = schema_name

    def drop_database(self, *, logger: Optional[Logger] = None) -> None:
        """
        Deletes the database

        :param logger: logger to use
        :return: None
        """
        self.run_query_with_schema(
            query=f"DROP DATABASE IF EXISTS {self.schema_name}",
            logger=logger,
            schema_name=None,
        )

    def create_database(self, *, logger: Optional[Logger] = None) -> None:
        """
        Creates the database

        :param logger: logger to use
        :return: None
        """
        self.run_query_with_schema(
            query=f"CREATE DATABASE IF NOT EXISTS {self.schema_name}",
            logger=logger,
            schema_name=None,
        )

    def recreate_database(self, *, logger: Optional[Logger] = None) -> None:
        """
        Recreates the database

        :param logger: logger to use
        :return: None
        """
        self.drop_database(logger=logger)
        self.create_database(logger=logger)

    def run_query(
        self, *, query: str, logger: Optional[Logger] = None
    ) -> Optional[int]:
        return self.run_query_with_schema(
            query=query, logger=logger, schema_name=self.schema_name
        )

    def run_query_with_schema(
        self,
        *,
        query: str,
        logger: Optional[Logger] = None,
        schema_name: Optional[str],
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[int]:
        """
        Runs the query


        :param query: query to run
        :param logger: logger to use
        :param schema_name: name of the schema to use
        :param params: parameters to pass to the query
        :return: number of rows affected
        """
        # noinspection PyUnresolvedReferences
        connection: pymysql.Connection[Cursor] = (
            pymysql.connect(
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                db=schema_name,
                client_flag=CLIENT.MULTI_STATEMENTS,
            )
            if schema_name
            else pymysql.connect(
                user=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                client_flag=CLIENT.MULTI_STATEMENTS,
            )
        )
        try:
            with connection.cursor() as cursor:
                sanitized_queries = self.sanitize_query(query)
                rows_affected: Optional[int] = 0
                for sanitized_query in sanitized_queries:
                    if logger:
                        logger.debug(f"Executing MySQL query: {sanitized_query}")
                    rows_affected = cursor.execute(sanitized_query, params)
                    connection.commit()
                return rows_affected

        except OperationalError as e:
            if logger:
                logger.error(f"Failed to run query {query}")
            raise e

        except MySQLError as e:
            if logger:
                logger.error("MySQL Error: ", e)
            connection.rollback()
            raise e

        finally:
            connection.close()

    def write_to_table(
        self,
        *,
        table_name: str,
        columns: List[str],
        data: List[Dict[str, Any]],
        logger: Optional[Logger] = None,
    ) -> Optional[int]:
        """
        Writes the data to the table

        :param table_name: name of the table to write to
        :param columns: list of columns to write
        :param data: list of dictionaries to write
        :param logger: logger to use
        :return: number of rows affected
        """
        # create the connection

        assert table_name, "table_name should not be None"
        assert columns, "columns should not be None"
        assert data, "data should not be None"
        assert isinstance(columns, list), "columns should be a list"
        assert isinstance(data, list), "data should be a list"
        if len(data) > 0:
            assert all(
                isinstance(d, dict) for d in data
            ), "data should be a list of dictionaries instead it is a list of " + str(
                [type(d) for d in data]
            )

        # noinspection PyUnresolvedReferences
        connection: Connection[Cursor] = pymysql.connect(
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            db=self.schema_name,
        )
        # Generate the SQL query
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        try:
            # Convert list of dictionaries to list of tuples, ensuring the order of values matches the order of columns
            data_tuples = [tuple(d[col] for col in columns) for d in data]

            with connection.cursor() as cursor:
                if logger:
                    logger.debug(f"Executing MySQL query: {query}")
                rows_affected: Optional[int] = 0
                for sanitized_query in self.sanitize_query(query):
                    # Execute the query
                    rows_affected = cursor.executemany(sanitized_query, data_tuples)
                    connection.commit()
                return rows_affected

        except OperationalError as e:
            if logger:
                logger.error(f"Failed to run query {query}")
            raise e

        except MySQLError as e:
            if logger:
                logger.error("MySQL Error: ", e)
            connection.rollback()
            raise e

        finally:
            connection.close()

    def read_from_table(
        self, *, table_name: str, columns: List[str]
    ) -> List[Dict[str, Any]]:
        # create the connection
        # noinspection PyUnresolvedReferences
        connection: Connection[Cursor] = pymysql.connect(
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            db=self.schema_name,
        )
        cursor: pymysql.cursors.DictCursor
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            query = f"SELECT * FROM {table_name}"
            for sanitized_query in self.sanitize_query(query):
                cursor.execute(sanitized_query)
            # dictionary cursor returns list of dictionaries
            rows: List[Dict[str, Any]] = cast(List[Dict[str, Any]], cursor.fetchall())
            return rows

    @staticmethod
    def sanitize_query(query: str) -> List[str]:
        """
        Sanitizes the query by formatting it with proper indentation and whitespace
        and using sqlparse to parse the query


        :param query: SQL
        :return: list of sanitized queries found in query string
        """
        sanitized_queries: List[str] = []
        # Parse the query
        for parsed_query in sqlparse.parse(query):
            # Format the query with proper indentation and whitespace
            formatted_query = sqlparse.format(
                str(parsed_query), reindent=True, keyword_case="upper"
            )

            # Strip any leading or trailing whitespace
            sanitized_query = formatted_query.strip()

            sanitized_queries.append(sanitized_query)

        return sanitized_queries

    def close(self) -> None:
        pass
