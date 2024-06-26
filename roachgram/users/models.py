from django.db import models
from django.contrib.auth.models import AbstractUser
import auto_prefetch
from datetime import datetime
# Create your models here.

def user_profile_directory(instance , filename):
    return f"{instance}/{filename}"

class User(AbstractUser):
    name    = models.CharField(max_length=255 , blank=True , null=True)
    email   = models.EmailField(unique=True)
    about   = models.TextField(max_length=255 , blank=True , null=True)
    profile = models.ImageField(upload_to=user_profile_directory , default="default-profile.png" , blank=True , null=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username
    
    def get_followers_and_followings_count(self):
        followersCount = FollowUser.objects.filter(following=self).count()
        followingsCount = FollowUser.objects.filter(follower=self).count()

        return {
            "followersCount": followersCount,
            "followingsCount": followingsCount
        }
    
    def get_all_user_posts(self):
        from feeds.models import Post  
        return Post.objects.filter(user=self).order_by("-createdAt")
    
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username)

class FollowUser(models.Model):
    follower = auto_prefetch.ForeignKey(User , on_delete=models.CASCADE , related_name="followers")
    following = auto_prefetch.ForeignKey(User , on_delete=models.CASCADE , related_name="followings")
    createdAt = models.TimeField(auto_now_add=True , blank=True , null=True)
    updatedAt = models.TimeField(auto_now=True , blank=True , null=True)


    def __str__(self):
        return f"{self.follower.username} following {self.following.username}"
    

class NotificationType(models.Model):
    TYPE_CHOICES = (
        ("LIKE" , "Like"),
        ("COMMENT" , "Comment"),
        ("MENTION" , "Mention"),
        ("FOLLOW" , "Follow"),
        ("MESSAGE" , "Message"),
        ("BOOKMARK" , "Bookmark")
    )
    type = models.CharField(
        choices=TYPE_CHOICES,
        max_length=128
    )
    text = models.TextField()

    def __str__(self) -> str:
        return f"{self.type} - {self.text}"

class Notification(models.Model):
    user_to_notif = models.ForeignKey(User , on_delete=models.CASCADE)
    notif_type = models.ForeignKey(NotificationType , on_delete=models.CASCADE)
    triggered_by = models.ForeignKey(User , on_delete=models.CASCADE , related_name="triggered_by")
    seen = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"notification for {self.user_to_notif.username}"