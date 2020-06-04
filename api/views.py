from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, filters

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import Post, Comment, Group, Follow, User
from .serializers import PostSerializer, CommentSerializer, GroupSerializer, FollowSerializer


class PostViewSet(ModelViewSet):

    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = Post.objects.all()
        group = self.request.query_params.get('group', None)
        if group is not None:
            queryset = queryset.filter(group=group)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if request.user == post.author:
            if serializer.is_valid():
                serializer.save(author=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        if request.user == post.author:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        queryset = Comment.objects.filter(post=post)
        return queryset

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return serializer.save(author=self.request.user, post=post)

    def partial_update(self, request, pk=None, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
        serializer = CommentSerializer(
            comment, data=request.data, partial=True)
        if request.user == comment.author:
            if serializer.is_valid():
                serializer.save(author=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
        if request.user == comment.author:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowViewSet(ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=following__username', "=user__username"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        following = self.request.data.get('following')
        following = User.objects.get(username=following)
        user = self.request.user

        followers = Follow.objects.filter(user=user, following=following)
        if followers:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.save(
            user=user,
            following=following
        )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
