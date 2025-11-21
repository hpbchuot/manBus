from typing import Dict, Any, List, Optional, Generic, TypeVar

T = TypeVar('T')

class PaginationMixin(Generic[T]):
    """
    Mixin providing pagination operations.
    Single Responsibility: Pagination
    """

    def paginate(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Paginate entities.

        Returns:
            {
                'items': List[T],
                'total': int,
                'page': int,
                'per_page': int,
                'pages': int
            }
        """
        filters = filters or {}

        # Get total count
        total = self.repository.count(filters)

        # Calculate pagination
        pages = (total + per_page - 1) // per_page
        offset = (page - 1) * per_page

        # Get paginated results
        entities = self.repository.paginate(
            limit=per_page,
            offset=offset,
            filters=filters,
            order_by=order_by
        )

        return {
            'items': [self._to_schema(e) for e in entities],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pages
        }