from django.db.models import Prefetch
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.models import Registration
from users.models import User
from users.serializers import ProfileSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.prefetch_related(
            Prefetch(
                "event_registrations",
                queryset=Registration.objects.order_by("-registered_at")[:10],
                to_attr="latest_registrations",
            )
        ).get(pk=request.user.id)

        serializer = ProfileSerializer(user)

        return Response(serializer.data)
