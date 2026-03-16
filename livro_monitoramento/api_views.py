from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny

from .models import Registro, LogAcao
from .serializers import RegistroSerializer
from .utils_auditoria import diff_registro


class ObtainTokenAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "Credenciais inválidas."}, status=status.HTTP_401_UNAUTHORIZED)

        is_api_group = user.groups.filter(name="api").exists()
        if not (user.is_staff or user.is_superuser or is_api_group):
            return Response({"detail": "Sem permissão para acessar a API."}, status=status.HTTP_403_FORBIDDEN)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class RegistroCreateAPIView(APIView):
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            registro = serializer.save(autor=request.user)
            LogAcao.objects.create(
                usuario=request.user,
                acao="CREATE",
                tipo=registro.tipo,
                registro_id=registro.pk,
                titulo=registro.titulo,
            )
            return Response(RegistroSerializer(registro).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistroUpdateAPIView(APIView):
    def patch(self, request, pk):
        try:
            registro = Registro.objects.get(pk=pk)
        except Registro.DoesNotExist:
            return Response({"detail": "Registro não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        old = Registro.objects.get(pk=pk)
        serializer = RegistroSerializer(registro, data=request.data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            detalhes = diff_registro(old, updated)
            if detalhes:
                LogAcao.objects.create(
                    usuario=request.user,
                    acao="UPDATE",
                    tipo=updated.tipo,
                    registro_id=updated.pk,
                    titulo=updated.titulo,
                    detalhes=detalhes,
                )
            return Response(RegistroSerializer(updated).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
