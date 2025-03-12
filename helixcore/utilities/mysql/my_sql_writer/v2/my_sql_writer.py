import logging
import os
from asyncio import Lock
from contextlib import nullcontext
from logging import Logger
from typing import Dict, Any, Optional, List, cast, AsyncContextManager, Tuple

import aiomysql
import sqlparse
from aiomysql import OperationalError, MySQLError, Pool
from pymysql import ProgrammingError

from helixcore.utilities.mysql.pydatabelt.mysql import (
    get_mysql_config,
    construct_mysql_connection_string,
)


class MySqlWriter:
    def __init__(self, *, schema_name: str, max_batch_size: Optional[int]) -> None:
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
        self._connection_pool: Optional[Pool] = None
        self.max_batch_size: Optional[int] = max_batch_size
        self._connection_pool_lock: Lock = Lock()

    async def get_connection_pool_async(self) -> Pool:
        async with self._connection_pool_lock:
            if self._connection_pool is None:
                self._connection_pool = await self.create_connection_pool(
                    schema_name=self.schema_name
                )
            return self._connection_pool

    async def open_async(self) -> None:
        pass

    async def drop_database_async(self, *, logger: Optional[Logger] = None) -> None:
        """
        Deletes the database

        :param logger: logger to use
        :return: None
        """
        await self.run_query_with_schema_async(
            query=f"DROP DATABASE IF EXISTS {self.schema_name}",
            logger=logger,
            schema_name=None,
        )

    async def create_database_async(self, *, logger: Optional[Logger] = None) -> None:
        """
        Creates the database

        :param logger: logger to use
        :return: None
        """
        await self.run_query_with_schema_async(
            query=f"CREATE DATABASE IF NOT EXISTS {self.schema_name}",
            logger=logger,
            schema_name=None,
        )

    async def recreate_database_async(self, *, logger: Optional[Logger] = None) -> None:
        """
        Recreates the database

        :param logger: logger to use
        :return: None
        """
        await self.drop_database_async(logger=logger)
        await self.create_database_async(logger=logger)

    async def run_query_async(
        self, *, query: str, logger: Optional[Logger] = None
    ) -> Optional[int]:
        return await self.run_query_with_schema_async(
            query=query, logger=logger, schema_name=self.schema_name
        )

    async def run_query_with_schema_async(
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
        connection: aiomysql.Connection
        context_manager: AsyncContextManager[aiomysql.Connection] = (
            (await self.get_connection_pool_async()).acquire()
            if schema_name
            else nullcontext(
                await aiomysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.username,
                    password=self.password,
                )
            )
        )
        async with context_manager as connection:
            try:
                cursor: aiomysql.cursors.Cursor
                async with connection.cursor() as cursor:
                    sanitized_queries = self.sanitize_query(query)
                    rows_affected: Optional[int] = 0
                    for sanitized_query in sanitized_queries:
                        if logger:
                            logger.debug(f"Executing MySQL query: {sanitized_query}")
                        rows_affected = await cursor.execute(sanitized_query, params)
                        await connection.commit()
                    return rows_affected

            except TypeError as e:
                if logger:
                    logger.error(f"Failed to run query {query}")
                raise e
            except OperationalError as e:
                if logger:
                    logger.error(f"Failed to run query {query}")
                raise e

            except MySQLError as e:
                if logger:
                    logger.error("MySQL Error: ", e)
                await connection.rollback()
                raise e

            finally:
                connection.close()

    async def write_to_table_async(
        self,
        *,
        table_name: str,
        columns: List[str],
        data: List[Dict[str, Any]],
        logger: Optional[Logger],
        create_table_ddl: Optional[str],
    ) -> Optional[int]:
        """
        Writes the data to the table

        :param table_name: name of the table to write to
        :param columns: list of columns to write
        :param data: list of dictionaries to write
        :param logger: logger to use
        :param create_table_ddl: DDL to create the table
        :return: number of rows affected
        """

        if len(data) == 0:
            return 0

        # divide the data into batches
        if self.max_batch_size:
            data_batches = [
                data[i : i + self.max_batch_size]
                for i in range(0, len(data), self.max_batch_size)
            ]
        else:
            data_batches = [data]

        # now write each batch
        rows_affected = 0
        for batch_index, data_batch in enumerate(data_batches):
            if logger and logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"Writing batch {batch_index} with {len(data_batch)} rows to {table_name}"
                )
            try:
                rows_affected += (
                    await self.write_batch_to_table_async(
                        table_name=table_name,
                        columns=columns,
                        data=data_batch,
                        logger=logger,
                        create_table_ddl=create_table_ddl,
                    )
                    or 0
                )
            except Exception as e:
                if logger:
                    logger.error(f"Failed to write batch {batch_index} to {table_name}")
                raise e
        return rows_affected

    async def write_batch_to_table_async(
        self,
        *,
        table_name: str,
        columns: List[str],
        data: List[Dict[str, Any]],
        create_table_ddl: Optional[str],
        logger: Optional[Logger] = None,
    ) -> Optional[int]:
        """
        Writes the data to the table

        :param table_name: name of the table to write to
        :param columns: list of columns to write
        :param data: list of dictionaries to write
        :param create_table_ddl: DDL to create the table
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
        connection_pool: Pool = await self.get_connection_pool_async()
        assert connection_pool is not None

        connection: aiomysql.Connection
        async with connection_pool.acquire() as connection:
            # Generate the SQL query
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
            try:
                # Convert list of dictionaries to list of tuples, ensuring the order of values matches the order of columns
                data_tuples: List[Tuple[Any, ...]] = [
                    tuple(d[col] for col in columns) for d in data
                ]

                return await self._run_query_with_connection(
                    connection=connection, data_tuples=data_tuples, query=query
                )

            except TypeError as e:
                if logger:
                    logger.error(f"Failed to run query {query}")
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"Data: {data}")
                raise e
            except ProgrammingError as e:
                if e.args[0] == 1146:
                    if logger:
                        logger.error(
                            f"Table {table_name} does not exist.  Please create the table before writing to it"
                        )
                        # run create table query
                        if create_table_ddl:
                            await self.run_query_with_schema_async(
                                query=create_table_ddl,
                                logger=logger,
                                schema_name=self.schema_name,
                            )
                            return await self._run_query_with_connection(
                                connection=connection,
                                data_tuples=data_tuples,
                                query=query,
                            )
                        else:
                            raise e
                    raise e
                if logger:
                    logger.error(f"Failed to run query {query}")
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"Data: {data}")
                raise e
            except OperationalError as e:
                if logger:
                    logger.error(f"Failed to run query {query}")
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"Data: {data}")
                raise e

            except MySQLError as e:
                if logger:
                    logger.error("MySQL Error: ", e)
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"Data: {data}")
                await connection.rollback()
                raise e

            finally:
                connection.close()

    async def _run_query_with_connection(
        self,
        *,
        connection: aiomysql.Connection,
        data_tuples: List[Tuple[Any, ...]],
        query: str,
    ) -> Optional[int]:
        cursor: aiomysql.cursors.Cursor
        async with connection.cursor() as cursor:
            rows_affected: Optional[int] = 0
            for sanitized_query in self.sanitize_query(query):
                # Execute the query
                rows_affected = await cursor.executemany(sanitized_query, data_tuples)
                await connection.commit()
            return rows_affected

    # noinspection PyUnusedLocal
    async def read_from_table_async(
        self, *, table_name: str, columns: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Reads the data from the table


        :param table_name:
        :param columns:
        :return: data read from the table
        """
        assert table_name, "table_name should not be None"
        connection_pool: Pool = await self.get_connection_pool_async()
        assert connection_pool is not None
        # create the connection
        connection: aiomysql.Connection
        async with connection_pool.acquire() as connection:
            cursor: aiomysql.cursors.DictCursor
            async with connection.cursor(aiomysql.cursors.DictCursor) as cursor:
                query = f"SELECT * FROM {table_name}"
                for sanitized_query in self.sanitize_query(query):
                    await cursor.execute(sanitized_query)
                # dictionary cursor returns list of dictionaries
                rows: List[Dict[str, Any]] = cast(
                    List[Dict[str, Any]], await cursor.fetchall()
                )
                return rows

    async def create_connection_pool(self, schema_name: Optional[str]) -> Pool:
        """
        Creates a connection pool to the database


        :param schema_name:
        :return:
        """
        pool: Pool = await aiomysql.create_pool(
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            db=schema_name,
            autocommit=False,
        )
        return pool

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

    async def close_async(self) -> None:
        if self._connection_pool is not None:
            self._connection_pool.close()
            await self._connection_pool.wait_closed()
