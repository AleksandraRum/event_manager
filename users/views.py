from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import ProfileSerializer


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        registrations = user.event_registrations.order_by("-registered_at")[:10]

        serializer = ProfileSerializer(
            user,
            context={"registrations": registrations},
        )

        return Response(serializer.data)
