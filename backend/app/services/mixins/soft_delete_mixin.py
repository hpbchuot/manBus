class SoftDeleteMixin:
    """
    Mixin providing soft delete operations.
    Single Responsibility: Soft Delete Management
    """

    def soft_delete(self, entity_id: int) -> bool:
        """Soft delete entity (sets deleted_at timestamp)"""
        return self.repository.soft_delete(entity_id)

    def restore(self, entity_id: int) -> bool:
        """Restore soft-deleted entity"""
        return self.repository.restore(entity_id)

    def is_deleted(self, entity_id: int) -> bool:
        """Check if entity is soft-deleted"""
        entity = self.repository.get_by_id(entity_id, include_deleted=True)
        return entity.get('deleted_at') is not None if entity else False