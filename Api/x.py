# class ModelClass (APIView):
#     permission_classes = [IsAuthenticated]

#     def get (self, request):
#         try:
#             check_account_type(request.user, account_type)
            
#         except PermissionDenied:
#             return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
