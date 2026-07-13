from rest_framework.pagination import CursorPagination, PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class FeedCursorPagination(CursorPagination):
    """Cursor pagination for unbounded, insert-at-head lists (feed, comments,
    replies). `OFFSET n` would make Postgres scan and discard n rows; a
    cursor is O(1) at any depth and stable under concurrent inserts.

    Ordering matches the `(-created_at, -id)` composite index exactly — the
    id tiebreaker is what keeps the cursor stable when multiple rows share
    a `created_at` value.
    """

    page_size = 20
    max_page_size = 100
    ordering = ("-created_at", "-id")


class ReplyCursorPagination(CursorPagination):
    """Cursor pagination for replies — read oldest-first (thread reading
    order), unlike the feed/top-level-comments lists which read
    newest-first. Ordering matches the `(parent, created_at ASC, id ASC)`
    index exactly.
    """

    page_size = 20
    max_page_size = 100
    ordering = ("created_at", "id")
