"""
Database connection and management
Provides connection pooling and query execution for PostgreSQL
"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class Database:
    """Database connection pool and query executor"""

    def __init__(self):
        """Initialize database connection pool"""
        try:
            # Get database configuration from environment
            self.db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'manBusDB'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'admin')
            }

            # Create connection pool
            self._pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                **self.db_config
            )

            if self._pool:
                logger.info(f"Database connection pool created successfully for {self.db_config['database']}")
            else:
                raise Exception("Failed to create connection pool")

        except Exception as e:
            logger.error(f"Error creating database connection pool: {e}")
            raise

    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return self._pool.getconn()
        except Exception as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise

    def return_connection(self, conn):
        """Return a connection to the pool"""
        try:
            self._pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error returning connection to pool: {e}")

    def execute_query(self, query, params=None):
        """
        Execute a query and return results

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Query results as list of dicts
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)

            # Check if query returns results (SELECT, RETURNING, etc.)
            if cursor.description:
                results = cursor.fetchall()
                conn.commit()
                return results
            else:
                # For INSERT, UPDATE, DELETE without RETURNING
                conn.commit()
                return None

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error executing query: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)

    def fetch_one(self, query, params=None):
        """
        Execute a query and return a single result

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Single result as dict or None
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.commit()
            return result

        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error fetching one: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)

    def fetch_all(self, query, params=None):
        """
        Execute a query and return all results

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of results as dicts
        """
        return self.execute_query(query, params)

    def check_health(self):
        """
        Check database connectivity

        Returns:
            bool: True if database is accessible, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            self.return_connection(conn)
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def close_all_connections(self):
        """Close all connections in the pool"""
        try:
            if self._pool:
                self._pool.closeall()
                logger.info("All database connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {e}")


# Backward compatibility - ConnectionPool class
class ConnectionPool:
    """Manages database connection pool only (deprecated - use Database)"""
    def __init__(self, database_instance):
        self._db = database_instance

    def get_connection(self):
        return self._db.get_connection()

    def return_connection(self, conn):
        return self._db.return_connection(conn)