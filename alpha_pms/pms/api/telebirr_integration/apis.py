from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from pms.api.telebirr_integration.apply_fabric_token_module import *


class ApplyFabricTokenView(APIView):
    permission_classes = []
    def get(self,request):
        result = apply_fabric_token()
        if result:
            return Response(result)
        return Response({"error":"failed to get fabric token"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)