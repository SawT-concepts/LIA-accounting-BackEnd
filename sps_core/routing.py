
# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/payroll/$', consumers.PayrollConsumer.as_asgi()),
    re_path(r'ws/virtual-account/<int:group_id>/', consumers.VirtualAccountConsumer.as_asgi()),
]
