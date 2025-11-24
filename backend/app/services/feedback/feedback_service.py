"""
Feedback Service - Following SOLID principles.

This service follows all SOLID principles:
- SRP: Only feedback-related business logic
- OCP: Extensible via composition
- LSP: Implements IFeedbackService
- ISP: Focused interface
- DIP: Depends on FeedbackRepository abstraction
"""
from typing import Optional, List, Dict, Any
from app.repositories.feedback_repository import FeedbackRepository


class FeedbackService:
    """
    Feedback Service - Handles feedback business logic.

    Follows SOLID principles:
    - SRP: Only feedback-related business logic (no ORM, no token parsing)
    - OCP: Can be extended without modification
    - LSP: Implements service contract
    - ISP: Focused interface with only necessary methods
    - DIP: Depends on FeedbackRepository abstraction, not concrete ORM
    """

    def __init__(self, feedback_repository: FeedbackRepository):
        """
        Dependency injection - depends on abstraction.

        Args:
            feedback_repository: Feedback repository instance
        """
        self.repository = feedback_repository

    # Create operations
    def create(self, user_id: int, bus_id: int, content: str) -> Optional[Dict[str, Any]]:
        """
        Create new feedback with validation.

        Args:
            user_id: User ID submitting feedback
            bus_id: Bus ID related to feedback
            content: Feedback content

        Returns:
            Created feedback dict or None if creation failed

        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if not content or len(content.strip()) < 10:
            raise ValueError("Feedback content must be at least 10 characters")

        if len(content) > 1000:
            raise ValueError("Feedback content must not exceed 1000 characters")

        # Create via repository
        entity_dict = self.repository.create({
            'user_id': user_id,
            'bus_id': bus_id,
            'content': content.strip()
        })

        return entity_dict

    # Read operations
    def get_by_id(self, feedback_id: int) -> Optional[Dict[str, Any]]:
        """
        Get feedback by ID.

        Args:
            feedback_id: Feedback ID

        Returns:
            Feedback dict or None if not found
        """
        return self.repository.get_by_id(feedback_id)

    def get_by_user(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all feedback submitted by a user.

        Args:
            user_id: User ID
            status: Optional status filter (Pending, In Review, Resolved, Rejected)

        Returns:
            List of feedback dicts with bus and route information
        """
        return self.repository.get_by_user(user_id, status)

    def get_by_bus(self, bus_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all feedback for a specific bus.

        Args:
            bus_id: Bus ID
            status: Optional status filter

        Returns:
            List of feedback dicts with user information
        """
        return self.repository.get_by_bus(bus_id, status)

    def get_by_route(self, route_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all feedback for buses on a specific route.

        Args:
            route_id: Route ID
            status: Optional status filter

        Returns:
            List of feedback dicts
        """
        return self.repository.get_by_route(route_id, status)

    def get_pending_feedback(self) -> List[Dict[str, Any]]:
        """
        Get all pending feedback (admin function).

        Returns:
            List of pending feedback dicts
        """
        return self.repository.get_pending_feedback()

    def get_all(
        self,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all feedback with optional filtering (admin function).

        Args:
            status: Optional status filter
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of feedback dicts
        """
        return self.repository.get_all(status, limit, offset)

    def get_recent_feedback(self, days: int = 7, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent feedback entries.

        Args:
            days: Number of days to look back
            limit: Maximum number of results

        Returns:
            List of recent feedback dicts
        """
        if days < 1:
            raise ValueError("Days must be at least 1")

        return self.repository.get_recent_feedback(days, limit)

    def get_statistics(self) -> List[Dict[str, Any]]:
        """
        Get feedback statistics (admin function).

        Returns:
            List of dicts with status counts
        """
        return self.repository.get_statistics()

    # Update operations
    def update_status(self, feedback_id: int, new_status: str) -> bool:
        """
        Update feedback status (admin function).

        Args:
            feedback_id: Feedback ID
            new_status: New status (Pending, In Review, Resolved, Rejected)

        Returns:
            True if update successful

        Raises:
            ValueError: If validation fails
        """
        # Business validation
        valid_statuses = ['Pending', 'In Review', 'Resolved', 'Rejected']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

        # Check existence
        feedback = self.repository.get_by_id(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback {feedback_id} not found")

        # Update via repository
        success = self.repository.update_status(feedback_id, new_status)
        if not success:
            raise ValueError(f"Failed to update feedback {feedback_id} status")

        return True

    def update_content(self, feedback_id: int, user_id: int, new_content: str) -> bool:
        """
        Update feedback content (user function - can only edit their own).

        Args:
            feedback_id: Feedback ID
            user_id: User ID for ownership verification
            new_content: New feedback content

        Returns:
            True if update successful

        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if not new_content or len(new_content.strip()) < 10:
            raise ValueError("Feedback content must be at least 10 characters")

        if len(new_content) > 1000:
            raise ValueError("Feedback content must not exceed 1000 characters")

        # Check existence and ownership
        feedback = self.repository.get_by_id(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback {feedback_id} not found")

        if feedback.get('user_id') != user_id:
            raise ValueError("You can only edit your own feedback")

        if feedback.get('status') != 'Pending':
            raise ValueError("You can only edit pending feedback")

        # Update via repository
        success = self.repository.update_content(feedback_id, user_id, new_content.strip())
        if not success:
            raise ValueError(f"Failed to update feedback {feedback_id} content")

        return True

    # Delete operations
    def delete(self, feedback_id: int, user_id: Optional[int] = None) -> bool:
        """
        Delete feedback.
        Users can only delete their own pending feedback.
        Admins (user_id=None) can delete any feedback.

        Args:
            feedback_id: Feedback ID
            user_id: User ID for ownership verification (None for admin)

        Returns:
            True if deletion successful

        Raises:
            ValueError: If validation fails
        """
        # Check existence
        feedback = self.repository.get_by_id(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback {feedback_id} not found")

        # Business rules for non-admin users
        if user_id is not None:
            if feedback.get('user_id') != user_id:
                raise ValueError("You can only delete your own feedback")

            if feedback.get('status') != 'Pending':
                raise ValueError("You can only delete pending feedback")

        # Delete via repository
        success = self.repository.delete(feedback_id, user_id)
        if not success:
            raise ValueError(f"Failed to delete feedback {feedback_id}")

        return True
