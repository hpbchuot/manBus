class DatabaseHealthChecker:
    """Checks database health only"""
    def __init__(self, connection_pool):
        self._pool = connection_pool
    
    def check_connection(self):
        pass