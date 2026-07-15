from apps.chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from apps.notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns

# Combination of all apps' websocket_urlpatterns.
websocket_urlpatterns = [
    *notifications_websocket_urlpatterns,
    *chat_websocket_urlpatterns,
]
