from django.contrib import admin
from .models import Post , Like , Media , Bookmark , Comment
# Register your models here.
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Media)
admin.site.register(Bookmark)
admin.site.register(Comment)