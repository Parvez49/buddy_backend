from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context) -> Response | None:
    """Reshape DRF's default error response into the {success, message, errors} envelope.

    Unhandled (non-APIException) exceptions still return None so they propagate
    normally — this only reshapes errors DRF already recognizes.
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    errors = response.data
    if isinstance(errors, list):
        errors = {"non_field_errors": errors}

    detail = errors.get("detail") if isinstance(errors, dict) else None
    message = str(detail) if detail is not None and len(errors) == 1 else "Validation failed."

    response.data = {"success": False, "message": message, "errors": errors}
    return response
