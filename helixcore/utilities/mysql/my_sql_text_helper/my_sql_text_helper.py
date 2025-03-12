from typing import Optional, List

MYSQL_TEXT_MAX_CHARACTERS = 64000  # 64KB
MYSQL_MEDIUMTEXT_MAX_CHARACTERS = 16 * 1000 * 1000  # 16MB
MYSQL_LONGTEXT_MAX_CHARACTERS = 4 * 1000 * 1000 * 1000  # 4GB


class MySqlTextHelper:
    @staticmethod
    def truncate(
        text: Optional[str], maximum_length: Optional[int] = None
    ) -> Optional[str]:
        """
        Truncates the provider text if it is longer than 64,000 characters to fit in TEXT field for MySQL.
        Handles null text


        :param text: text to check for length
        :param maximum_length: max length to truncate to
        :return truncated text
        """
        if text is None:
            return None
        if maximum_length is not None:
            return text[:maximum_length]
        if len(text) > MYSQL_TEXT_MAX_CHARACTERS:
            return text[:MYSQL_TEXT_MAX_CHARACTERS]
        else:
            return text

    @staticmethod
    def convert_list_to_sql_list(my_list: Optional[List[str]]) -> str:
        return ",".join([f"'{r}'" for r in my_list]) if my_list else ""
