def envelope_postprocessing_hook(result, generator, request, public):
    """Rewrap every operation's response schema in the {success, message,
    data|errors} shape that `EnvelopeJSONRenderer` actually returns.

    Without this, drf-spectacular documents the raw serializer output as the
    response body, which isn't what a client ever receives — every response
    is wrapped by the renderer first.
    """
    for path_item in result.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict) or "responses" not in operation:
                continue
            for status_code, response in operation["responses"].items():
                content = response.get("content")
                if not content:
                    continue
                is_error = str(status_code).startswith(("4", "5"))
                envelope_key = "errors" if is_error else "data"
                for media_object in content.values():
                    inner_schema = media_object.get("schema")
                    if inner_schema is None:
                        continue
                    media_object["schema"] = {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean", "example": not is_error},
                            "message": {"type": "string", "nullable": True},
                            envelope_key: inner_schema,
                        },
                        "required": ["success", "message", envelope_key],
                    }
    return result
