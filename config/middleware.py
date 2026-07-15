from urllib.parse import parse_qs

from channels.auth import AuthMiddleware, UserLazyObject
from channels.db import database_sync_to_async


@database_sync_to_async
def get_user(scope):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """
    # postpone model import to avoid ImproperlyConfigured error before Django
    # setup is complete.
    from django.contrib.auth.models import AnonymousUser
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

    if "query_params" not in scope:
        raise ValueError(
            "Cannot find query_params in scope. You should wrap your consumer in "
            "QueryParamsMiddleware."
        )

    try:
        # Re-use authentication class from simplejwt to validate the token.
        jwt_auth = JWTAuthentication()

        raw_token = scope["query_params"]["access_token"][0]
        validated_token = jwt_auth.get_validated_token(raw_token=raw_token)
        user = jwt_auth.get_user(validated_token)

    except (KeyError, InvalidToken, TokenError):
        user = None

    return user or AnonymousUser()


class QueryParamsMiddleware:
    """
    Extracts query parameters from the scope['query_string'] and adds them to
    scope['query_params'] as a dictionary.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Parse query string
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)

        # Add query_params to scope
        scope["query_params"] = query_params

        # Return inner application
        return await self.inner(scope, receive, send)


class JWTAuthMiddleware(AuthMiddleware):
    """
    Middleware that populates scope['user'] from a JWT token in the query params.
    Requires QueryParamsMiddleware to function.
    """

    def populate_scope(self, scope):
        # Make sure we have query_params in the scope
        if "query_params" not in scope:
            raise ValueError(
                "JWTAuthMiddleware cannot find query_params in scope. "
                "QueryParamsMiddleware must be above it."
            )
        if "user" not in scope:
            scope["user"] = UserLazyObject()

    async def resolve_scope(self, scope):
        # noinspection PyProtectedMember
        scope["user"]._wrapped = await get_user(scope)


def JWTAuthMiddlewareStack(inner):
    return QueryParamsMiddleware(JWTAuthMiddleware(inner))
