from .base_repository import BaseRepository

class UserRepository(BaseRepository):
    """User-specific repository - substitutable for BaseRepository"""

    def _get_table_name(self):
        return 'users'

    def _get_id_column(self):
        return 'id'

    def create(self, entity):
        """Create a new user using fn_create_user function"""
        query = '''
            SELECT fn_create_user(%s, %s, %s, %s, %s, %s) AS result
        '''
        params = (
            entity.get('name'),
            entity.get('phone'),
            entity.get('email'),
            entity.get('username'),
            entity.get('password'),
            entity.get('admin', False)
        )
        result = self._execute_query(query, params)
        if result:
            # Return the newly created user by ID
            return self.get_by_id(result[0]['result'])
        return None

    def update(self, entity):
        """Update an existing user using fn_update_user_profile function"""
        query = '''
            SELECT fn_update_user_profile(%s, %s, %s, %s, %s) AS result
        '''
        params = (
            entity.get('id'),
            entity.get('name'),
            entity.get('phone'),
            entity.get('email'),
            entity.get('username')
        )
        result = self._execute_query(query, params)
        if result and result[0]['result']:
            # Return the updated user
            return self.get_by_id(entity.get('id'))
        return None

    def verify_password(self, email_or_username, password):
        """Verify user password using fn_verify_user_password function"""
        query = '''
            SELECT fn_verify_user_password(%s, %s) AS user_id
        '''
        params = (email_or_username, password)
        result = self._execute_query(query, params)
        if result and result[0]['user_id']:
            user_row = self.get_by_id(result[0]['user_id'])[0]
            return dict(user_row)
        return None

    def change_password(self, user_id, new_password):
        """Change user password using fn_change_user_password function"""
        query = '''
            SELECT fn_change_user_password(%s, %s) AS result
        '''
        params = (user_id, new_password)
        result = self._execute_query(query, params)
        return result and result[0]['result']

    def soft_delete(self, user_id):
        """Soft delete a user using fn_soft_delete_user function"""
        query = '''
            SELECT fn_soft_delete_user(%s) AS result
        '''
        result = self._execute_query(query, (user_id,))
        return result and result[0]['result']

    def restore(self, user_id):
        """Restore a soft-deleted user using fn_restore_user function"""
        query = '''
            SELECT fn_restore_user(%s) AS result
        '''
        result = self._execute_query(query, (user_id,))
        return result and result[0]['result']
    
    def get_by_id(self, id):
        """Get user by ID"""
        query = 'SELECT id, name, phone, email, username, public_id FROM users WHERE id = %s AND is_deleted = FALSE'
        return self._execute_query(query, (id,))

    def get_by_email(self, email):
        """User-specific method: get user by email"""
        query = 'SELECT * FROM users WHERE email = %s AND is_deleted = FALSE'
        return self._execute_query(query, (email,))

    def get_active_users(self):
        """Get all active users using fn_get_active_users function"""
        query = 'SELECT * FROM fn_get_active_users()'
        return self._execute_query(query, None)

    def search_users(self, search_term):
        """Search users using fn_search_users function"""
        query = '''
            SELECT * FROM fn_search_users(%s)
        '''
        return self._execute_query(query, (search_term,))

    def get_by_public_id(self, public_id):
        """Get user by public_id using fn_get_user_by_public_id function"""
        query = '''
            SELECT * FROM fn_get_user_by_public_id(%s)
        '''
        result = self._execute_query(query, (public_id,))
        return result[0] if result else None

    def get_user_count(self):
        """Get count of active users using fn_get_user_count function"""
        query = 'SELECT fn_get_user_count() AS count'
        result = self._execute_query(query, None)
        return result[0]['count'] if result else 0