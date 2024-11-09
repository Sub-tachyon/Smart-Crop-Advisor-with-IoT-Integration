import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from prediction.routing import websocket_urlpatterns  # Adjust based on your app structure

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Crop_predictor.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
