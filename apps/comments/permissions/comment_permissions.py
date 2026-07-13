from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwner(BasePermission):
    """Safe methods are already gated by visibility upstream (the selector
    404s a comment on a private post before this ever runs); only unsafe
    methods need an ownership check here.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return obj.author_id == request.user.id
