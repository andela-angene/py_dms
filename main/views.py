from django.http import HttpResponse
from rest_framework import generics, permissions, status
from .serializers import RoleSerializer, UserSerializer, DocumentSerializer
from .models import Role, User, Document
from .helpers import paginate

from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsProfileOwnerOrAdmin, IsAppAdmin, IsDocumentOwner
from rest_framework.authtoken.models import Token


def index(req):
    return HttpResponse('Hello and welcome to PyDMS.')


# Roles
class RoleList(generics.ListCreateAPIView):
    """List all ROLES or create a new Role"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [
                permissions.IsAuthenticated, permissions.IsAdminUser]
        return super(self.__class__, self).get_permissions()


class RoleDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """Handles the http GET, PUT and DELETE requests"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (permissions.IsAuthenticated, IsAppAdmin)


# Users
class UserList(APIView):
    """List all users or create a new User"""
    def get(self, req, format=None):
        total = User.objects.count()
        params = req.query_params
        limit = int(params.get('limit', 20))
        offset = int(params.get('offset', 0))

        users = User.objects.all()[offset:offset + limit]
        serializer = UserSerializer(users, many=True)
        meta_data = paginate(total, limit, offset)
        return Response({'rows': serializer.data, 'meta_data': meta_data})

    def post(self, req, format=None):
        serializer = UserSerializer(data=req.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            token = Token.objects.create(
                user=User.objects.get(username=req.data['username']))
            data['token'] = token.key
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, Update or Delete a User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsProfileOwnerOrAdmin)


# Documents
class DocumentList(APIView):
    """List Documents or create a new Document"""
    def get(self, req, format=None):
        total = Document.objects.count()
        params = req.query_params
        limit = int(params.get('limit', 20))
        offset = int(params.get('offset', 0))

        documents = Document.objects.all()[offset:offset + limit]
        serializer = DocumentSerializer(documents, many=True)
        meta_data = paginate(total, limit, offset)
        return Response({'rows': serializer.data, 'meta_data': meta_data})

    def post(self, req, format=None):
        serializer = DocumentSerializer(data=req.data)
        if serializer.is_valid():
            serializer.save(author=req.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.IsAuthenticated]
        return super(self.__class__, self).get_permissions()


class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, Update or Delete a Document"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated,
                                       IsDocumentOwner]
        return super(self.__class__, self).get_permissions()
