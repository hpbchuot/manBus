from abc import ABC, abstractmethod
from typing import Optional, List
from app.schemas.feedback_schemas import (
    FeedbackResponse, FeedbackDetailResponse, FeedbackCreate,
    FeedbackUpdate, FeedbackStatusUpdate, FeedbackStats
)


class IFeedbackService(ABC):
    """
    Interface for Feedback Service following Interface Segregation Principle (ISP).
    Defines contract for feedback-related business operations.
    """

    @abstractmethod
    def get_by_id(self, feedback_id: int) -> Optional[FeedbackDetailResponse]:
        """
        Get feedback by ID with related information.

        Args:
            feedback_id: Feedback ID

        Returns:
            FeedbackDetailResponse or None if not found
        """
        pass

    @abstractmethod
    def get_by_user(self, user_id: int) -> List[FeedbackResponse]:
        """
        Get all feedback submitted by a user.

        Args:
            user_id: User ID

        Returns:
            List of feedback by user
        """
        pass

    @abstractmethod
    def get_by_bus(self, bus_id: int) -> List[FeedbackResponse]:
        """
        Get all feedback for a specific bus.

        Args:
            bus_id: Bus ID

        Returns:
            List of feedback for bus
        """
        pass

    @abstractmethod
    def get_all(self, status: Optional[str] = None) -> List[FeedbackResponse]:
        """
        Get all feedback with optional status filter.

        Args:
            status: Optional status filter (Pending, Reviewed, Resolved, Dismissed)

        Returns:
            List of feedback
        """
        pass

    @abstractmethod
    def create(self, feedback_data: FeedbackCreate, user_id: int) -> Optional[FeedbackResponse]:
        """
        Create new feedback.

        Args:
            feedback_data: Feedback creation data
            user_id: User ID (from authentication)

        Returns:
            Created FeedbackResponse or None if creation failed
        """
        pass

    @abstractmethod
    def update(self, feedback_id: int, feedback_data: FeedbackUpdate) -> Optional[FeedbackResponse]:
        """
        Update feedback.

        Args:
            feedback_id: Feedback ID
            feedback_data: Updated feedback data

        Returns:
            Updated FeedbackResponse or None if update failed
        """
        pass

    @abstractmethod
    def update_status(self, feedback_id: int, status_data: FeedbackStatusUpdate) -> bool:
        """
        Update feedback status (admin only).

        Args:
            feedback_id: Feedback ID
            status_data: New status

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, feedback_id: int) -> bool:
        """
        Delete feedback.

        Args:
            feedback_id: Feedback ID

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_average_rating(self, bus_id: int) -> float:
        """
        Get average rating for a bus.

        Args:
            bus_id: Bus ID

        Returns:
            Average rating (0.0 if no ratings)
        """
        pass

    @abstractmethod
    def get_statistics(self, bus_id: Optional[int] = None) -> FeedbackStats:
        """
        Get feedback statistics.

        Args:
            bus_id: Optional bus ID filter

        Returns:
            Feedback statistics
        """
        pass
