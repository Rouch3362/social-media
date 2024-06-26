from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view , parser_classes
from .serializers import (
                        CreateUserSerializer , 
                        UpdateUserSeralizer , 
                        ChangePasswordSerializer ,
                        UserSerializer,
                        FollowSerializer,
                        NotificationSerializer
                        )
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import User , FollowUser , Notification as dbNotification
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.generics import UpdateAPIView , ListAPIView , RetrieveAPIView , CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import CursorPagination
from rest_framework.filters import SearchFilter
from rest_framework.views import Http404
from feeds.api.serializers import PostSerializer , GetCommentSerializer
from feeds.models import Like , Post , Comment
from feeds.api.viewsets import PostCursorPagination

class MyTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)


        token['name']     = user.name
        token['username'] = user.username
        token["profile"]  = user.profile.url
        token["about"]    = user.about
        token["email"]    = user.email

        return token
    
class MyToken(TokenObtainPairView):
    serializer_class = MyTokenSerializer



class UserCursorPagination(CursorPagination):
    ordering = "-date_joined"
    page_size = 10


class NotificationCursorPaginations(CursorPagination):
    ordering = "-createdAt"
    page_size = 10

class AllUsers(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = [SearchFilter,]
    search_fields = ["username" , "name" , "about"]
    pagination_class = UserCursorPagination

    
class OneUser(RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

class Notifications(ListAPIView):
    permission_classes = [IsAuthenticated,]
    pagination_class = NotificationCursorPaginations
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return dbNotification.objects.filter(user_to_notif=self.request.user)

class OneUserFollowers(ListAPIView):
    serializer_class = UserSerializer

    lookup_field = "username"

    pagination_class = UserCursorPagination

    def get_queryset(self):
        username = self.kwargs["username"]
        
        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            raise Http404

        followers = User.objects.filter(followers__in=FollowUser.objects.filter(following=user))
        return followers
    

class OneUserFollowings(ListAPIView):
    serializer_class = UserSerializer

    lookup_field = "username"

    pagination_class = UserCursorPagination

    def get_queryset(self):
        username = self.kwargs["username"]
        
        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            raise Http404

        followings = User.objects.filter(followings__in=FollowUser.objects.filter(follower=user))
        return followings


class OneUserLikes(ListAPIView):
    pagination_class = PostCursorPagination
    serializer_class = PostSerializer
    lookup_field = "username"

    def get_queryset(self):
        username = self.kwargs["username"]
        
        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            raise Http404
        
        LikedPosts = Post.objects.filter(post__in=Like.objects.filter(user=user.id))
        

        return LikedPosts
        

class OneUserReplies(ListAPIView):
    pagination_class = PostCursorPagination
    serializer_class = GetCommentSerializer
    lookup_field = "username"

    def get_queryset(self):
        username = self.kwargs["username"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        
        replies = Comment.objects.filter(user=user)

        return replies
    
        


class RegisterUser(CreateAPIView):
    serializer_class = CreateUserSerializer


    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()

class UserView(APIView):

    
    def delete(self , request , format=None):
        self.check_object_permissions(request , request.user)
        
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response({"message": "user not found"} , status=status.HTTP_404_NOT_FOUND)
        
        user.delete()

        return Response({"message": "user deleted successfully"}, status=status.HTTP_200_OK)

    

class UpdateUser(UpdateAPIView):
    serializer_class = UpdateUserSeralizer
    permission_classes = [IsAuthenticated,]


    def get_queryset(self):
        return self.request.user


    def update(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance , data=request.data , partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(UpdateAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        old_pass = request.data.get("old_password")
        new_pass = request.data.get("new_password")

        if serializer.is_valid():
            if not user.check_password(old_pass):
              return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_pass)
            user.save()
            return Response({'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully'})
          
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class FollowView(APIView):
    
    permission_classes = [IsAuthenticated,]


    def post(self , request , format=None):

        followInstance = FollowUser.objects.filter(follower=request.user , following=request.data["following"])

        if followInstance.exists():
            return Response({"message": "the authorized user is already following this user"} , status=status.HTTP_409_CONFLICT)

        if request.data["following"] == request.user.id:
            return Response({"message": "you can not follow yourself"} , status=status.HTTP_400_BAD_REQUEST)

        request.data["follower"] = request.user.id
        serializer = FollowSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self , request , format=None):
        try:
            followInstance = FollowUser.objects.get(follower=request.user , following=request.data["following"])
        except FollowUser.DoesNotExist:
            return Response({"message": "follower is not following this user"},status=status.HTTP_404_NOT_FOUND)

        followInstance.delete()

        return Response({"message": "unfollowed successfully"},status=status.HTTP_204_NO_CONTENT)