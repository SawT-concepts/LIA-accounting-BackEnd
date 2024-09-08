from rest_framework import generics
from ..models import Announcement
from .serializers import AnnouncementSerializer
from drf_yasg.utils import swagger_auto_schema

class AnnouncementList(generics.ListAPIView):
    queryset = Announcement.objects.filter(active=True)
    serializer_class = AnnouncementSerializer
    pagination_class = None 

    @swagger_auto_schema(operation_summary="List all active announcements")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
