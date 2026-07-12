from rest_framework.renderers import JSONRenderer


class EnvelopeJSONRenderer(JSONRenderer):
    """Wrap every response in a consistent {success, message, data|errors} envelope."""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")
        status_code = getattr(response, "status_code", 200)
        success = status_code < 400

        if (
            data is not None
            and "success" in data
            and ("data" in data or "errors" in data)
        ):
            # Already enveloped (e.g. by the custom exception handler) — pass through.
            envelope = data
        elif success:
            envelope = {"success": True, "message": None, "data": data}
        else:
            envelope = {"success": False, "message": None, "errors": data}

        return super().render(envelope, accepted_media_type, renderer_context)
