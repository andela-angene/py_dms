from django.http import HttpResponse
from rest_framework import generics, permissions, status
from .serializers import RoleSerializer, UserSerializer, DocumentSerializer
from .models import Role, User, Document
from .helpers import paginate, get_query_vars

from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsProfileOwnerOrAdmin, IsAppAdmin, IsDocumentOwner
from rest_framework_jwt.settings import api_settings
from django.db.models import Q
from django.shortcuts import render


def index(req):
    return render(req, 'index.html')

def documentation(req):
    return render(req, 'api.html')


# Roles
class RoleList(generics.ListCreateAPIView):
    """List all ROLES or create a new Role"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [
                permissions.IsAuthenticated, IsAppAdmin]
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
        limit, offset, search = get_query_vars(req.query_params)

        users = User.objects.all().filter(username__contains=search)
        total = users.count()
        serializer = UserSerializer(users[offset:offset + limit], many=True)
        meta_data = paginate(total, limit, offset)
        return Response({'rows': serializer.data, 'meta_data': meta_data})

    def post(self, req, format=None):
        serializer = UserSerializer(data=req.data)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(
                user=User.objects.get(username=req.data['username']))
            token = jwt_encode_handler(payload)

            data['token'] = token
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, Update or Delete a User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsProfileOwnerOrAdmin)

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super(self.__class__, self).get_serializer(*args, **kwargs)


# Documents
class DocumentList(APIView):
    """List Documents or create a new Document"""
    def get(self, req, format=None):
        limit, offset, search = get_query_vars(req.query_params)

        if not req.user.is_authenticated:
            documents = Document.objects.filter(access='public')
        elif req.user.role_id == Role.objects.get(name='admin'):
            documents = Document.objects.all()
        else:
            documents = Document.objects.filter(
                Q(access='public') | Q(author_id=req.user.id)
            )
        documents = documents.filter(title__contains=search).order_by(
            '-updated_at')
        total = documents.count()

        serializer = DocumentSerializer(
            documents[offset:offset + limit], many=True)
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


class UserDocuments(APIView):
    """List a User's Documents"""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, req, pk, format=None):
        limit, offset, search = get_query_vars(req.query_params)

        documents = Document.objects.filter(author_id=pk)
        documents = documents.filter(title__contains=search)
        total = documents.count()

        serializer = DocumentSerializer(
            documents[offset:offset + limit], many=True)
        meta_data = paginate(total, limit, offset)
        return Response(serializer.data)
