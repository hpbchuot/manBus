class DatabaseExecutor:
    """Executes database queries only"""
    def __init__(self, connection_pool):
        self._pool = connection_pool
    
    def execute_query(self, query, params):
        pass
    
    def execute_transaction(self, queries):
        pass