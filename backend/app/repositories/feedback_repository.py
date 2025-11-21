from typing import Optional, List, Dict, Any
from .base_repository import BaseRepository


class FeedbackRepository(BaseRepository):
    """
    Repository for Feedback entity.
    Encapsulates all data access logic for feedback using PostgreSQL functions.
    Follows Repository Pattern and DIP (Dependency Inversion Principle).
    """

    def _get_table_name(self) -> str:
        """Return the feedback table name"""
        return 'Feedback'

    def _get_id_column(self) -> str:
        """Return the primary key column name"""
        return 'id'

    # Create
    def create(self, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create feedback using PostgreSQL function.

        Args:
            entity: Dict with keys: user_id, bus_id, content

        Returns:
            Created feedback as dict or None
        """
        query = 'SELECT fn_create_feedback(%s, %s, %s) AS result'
        params = (
            entity.get('user_id'),
            entity.get('bus_id'),
            entity.get('content')
        )
        result = self._execute_query(query, params, fetch_one=True)

        if result and result.get('result'):
            return self.get_by_id(result['result'])
        return None

    # Read operations
    def get_by_id(self, feedback_id: int) -> Optional[Dict[str, Any]]:
        """
        Get feedback by ID.

        Args:
            feedback_id: Feedback ID

        Returns:
            Feedback dict or None if not found
        """
        query = 'SELECT * FROM Feedback WHERE id = %s'
        return self._execute_query(query, (feedback_id,), fetch_one=True)

    def get_by_user(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all feedback by user using PostgreSQL function.

        Args:
            user_id: User ID
            status: Optional status filter

        Returns:
            List of feedback dicts with bus and route information
        """
        query = 'SELECT * FROM fn_get_feedback_by_user(%s, %s)'
        return self._execute_query(query, (user_id, status), fetch_one=False)

    def get_by_bus(self, bus_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all feedback for a bus using PostgreSQL function.

        Args:
            bus_id: Bus ID
            status: Optional status filter

        Returns:
            List of feedback dicts with user information
        """
        query = 'SELECT * FROM fn_get_feedback_by_bus(%s, %s)'
        return self._execute_query(query, (bus_id, status), fetch_one=False)

    def get_by_route(self, route_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all feedback for buses on a route using PostgreSQL function.

        Args:
            route_id: Route ID
            status: Optional status filter

        Returns:
            List of feedback dicts
        """
        query = 'SELECT * FROM fn_get_feedback_by_route(%s, %s)'
        return self._execute_query(query, (route_id, status), fetch_one=False)

    def get_pending_feedback(self) -> List[Dict[str, Any]]:
        """
        Get all pending feedback using PostgreSQL function.

        Returns:
            List of pending feedback dicts with user, bus, and route information
        """
        query = 'SELECT * FROM fn_get_pending_feedback()'
        return self._execute_query(query, (), fetch_one=False)

    def get_all(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all feedback with optional filtering using PostgreSQL function.

        Args:
            status: Optional status filter
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of feedback dicts
        """
        query = 'SELECT * FROM fn_get_all_feedback(%s, %s, %s)'
        return self._execute_query(query, (status, limit, offset), fetch_one=False)

    def get_recent_feedback(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent feedback entries using PostgreSQL function.

        Args:
            days: Number of days to look back
            limit: Maximum number of results

        Returns:
            List of recent feedback dicts
        """
        query = 'SELECT * FROM fn_get_recent_feedback(%s, %s)'
        return self._execute_query(query, (days, limit), fetch_one=False)

    def get_statistics(self) -> List[Dict[str, Any]]:
        """
        Get feedback statistics using PostgreSQL function.

        Returns:
            List of dicts with status counts
        """
        query = 'SELECT * FROM fn_get_feedback_stats()'
        return self._execute_query(query, (), fetch_one=False)

    # Update operations
    def update(self, feedback_id: int, entity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update feedback.

        Args:
            feedback_id: Feedback ID
            entity: Dict with updated feedback data

        Returns:
            Updated feedback dict or None
        """
        # Handle content update separately if user_id is provided for ownership verification
        if 'content' in entity and 'user_id' in entity:
            success = self.update_content(feedback_id, entity['user_id'], entity['content'])
            if not success:
                return None

        # Handle status update
        if 'status' in entity:
            success = self.update_status(feedback_id, entity['status'])
            if not success:
                return None

        return self.get_by_id(feedback_id)

    def update_status(self, feedback_id: int, new_status: str) -> bool:
        """
        Update feedback status using PostgreSQL function.

        Args:
            feedback_id: Feedback ID
            new_status: New status (Pending, In Review, Resolved, Rejected)

        Returns:
            True if update successful, False otherwise
        """
        query = 'SELECT fn_update_feedback_status(%s, %s) AS result'
        result = self._execute_query(query, (feedback_id, new_status), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    def update_content(self, feedback_id: int, user_id: int, new_content: str) -> bool:
        """
        Update feedback content using PostgreSQL function (user edits).

        Args:
            feedback_id: Feedback ID
            user_id: User ID for ownership verification
            new_content: New feedback content

        Returns:
            True if update successful, False otherwise
        """
        query = 'SELECT fn_update_feedback_content(%s, %s, %s) AS result'
        result = self._execute_query(query, (feedback_id, user_id, new_content), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN

    # Delete
    def delete(self, feedback_id: int, user_id: Optional[int] = None) -> bool:
        """
        Delete feedback using PostgreSQL function.
        Users can only delete their own pending feedback.
        Admin (user_id=None) can delete any feedback.

        Args:
            feedback_id: Feedback ID
            user_id: User ID for ownership verification, None for admin

        Returns:
            True if deletion successful, False otherwise
        """
        query = 'SELECT fn_delete_feedback(%s, %s) AS result'
        result = self._execute_query(query, (feedback_id, user_id), fetch_one=True)
        return result.get('result', False) if result else True  # Function returns BOOLEAN
