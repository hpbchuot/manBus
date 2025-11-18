# Database connection pool

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import time
import logging
from contextlib import contextmanager

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _pool = None

    def __new__(cls):
        """Implement singleton pattern to ensure only one database instance"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._pool is not None:
            return

        # Database configuration
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = os.getenv('DB_PORT', '5432')
        self.DB_NAME = os.getenv('DB_NAME', 'TransitDB')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')

        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool with retries"""
        retries = 5
        while retries > 0:
            try:
                self._pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=20,
                    host=self.DB_HOST,
                    port=self.DB_PORT,
                    database=self.DB_NAME,
                    user=self.DB_USER,
                    password=self.DB_PASSWORD,
                    cursor_factory=RealDictCursor
                )
                logger.info(f"Database connection pool established")
                return
            except psycopg2.OperationalError as e:
                logger.error(f"Database connection pool initialization failed: {e}")
                retries -= 1
                if retries > 0:
                    logger.info(f"Retrying in 2 seconds... ({retries} attempts remaining)")
                    time.sleep(2)

        logger.critical("Could not initialize database connection pool after several attempts")
        raise Exception("Database connection pool initialization failed")

    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool as a context manager
        Automatically returns the connection to the pool after use
        """
        conn = None
        try:
            if self._pool is None:
                self._initialize_pool()
            conn = self._pool.getconn()
            if conn:
                yield conn
            else:
                raise Exception("Unable to get connection from pool")
        except psycopg2.OperationalError as e:
            logger.error(f"Connection error: {e}")
            raise
        finally:
            if conn:
                self._pool.putconn(conn)

    @contextmanager
    def get_cursor(self, commit=False):
        """
        Get a cursor as a context manager
        Args:
            commit: If True, commits the transaction after successful execution
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                cursor.close()

    def query(self, query, params=None, fetch=True):
        """
        Execute a SELECT query and return the results
        Args:
            query: SQL query string
            params: Query parameters
            fetch: If True, fetches and returns results
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    return result
                return None
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def execute(self, query, params=None):
        """
        Execute an INSERT/UPDATE/DELETE query
        Returns the number of affected rows
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.execute(query, params)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Execute query failed: {e}")
            raise

    def execute_many(self, query, params_list):
        """
        Execute multiple INSERT/UPDATE/DELETE queries in a single transaction
        Args:
            query: SQL query string
            params_list: List of parameter tuples
        Returns the number of affected rows
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.executemany(query, params_list)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Execute many failed: {e}")
            raise

    def fetch_one(self, query, params=None):
        """
        Execute a query and return a single result
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Fetch one failed: {e}")
            raise

    def check_health(self):
        """
        Check if the database connection is healthy
        Returns True if healthy, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def close_all_connections(self):
        """Close all connections in the pool"""
        if self._pool:
            self._pool.closeall()
            logger.info("All database connections closed")
            self._pool = None
    

    