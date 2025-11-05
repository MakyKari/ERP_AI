import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DatabaseConnection:

    def __init__(self, connection_string: str):
        """
        Args:
            connection_string: PostgreSQL connection string
                Формат: postgresql://user:password@host:port/dbname
        """
        self.connection_string = connection_string
        self.conn = None
        self.cursor = None
        self._parse_connection_string()
    
    def _parse_connection_string(self):
        """Парсит connection string и валидирует"""
        try:
            result = urlparse(self.connection_string)
            self.config = {
                'dbname': result.path[1:],  # убираем начальный /
                'user': result.username,
                'password': result.password,
                'host': result.hostname,
                'port': result.port or 5432
            }
            logger.info(f"Подключение к БД: {self.config['user']}@{self.config['host']}:{self.config['port']}/{self.config['dbname']}")
        except Exception as e:
            logger.error(f"Ошибка парсинга connection string: {e}")
            raise ValueError(f"Неверный формат connection string: {e}")
    
    def __enter__(self):
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            return self.cursor
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
            logger.error(f"Transaction rolled back: {exc_val}")
        else:
            self.conn.commit()
        
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()