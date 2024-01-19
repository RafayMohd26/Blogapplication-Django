from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager

# Create your models here.
class PublishedManager(models.Manager):
    def get_queryset(self) -> QuerySet:
      return super().get_queryset()\
        .filter(status=Post.Status.PUBLISHED)
    

class Post(models.Model):
  tags = TaggableManager()

  class Status(models.TextChoices):
    DRAFT = 'DF' , 'draft'
    PUBLISHED = 'PB' , 'published'

  

  title = models.CharField(max_length = 100)
  slug = models.SlugField(max_length = 200, unique_for_date = 'publish')
  author = models.ForeignKey(User,on_delete = models.CASCADE,related_name = 'blog_posts')
  body = models.TextField()
  publish = models.DateTimeField(default = timezone.now)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  status = models.CharField(max_length = 2 , choices = Status.choices , default = Status.DRAFT )
  objects = models.Manager()
  published = PublishedManager()
  

  class meta:
    ordering = ['-publish']
    indexes = [
      models.Index(fields=['-publish']),
    ]

  def __str__(self) -> str:
    return self.title
  
  def get_absolute_url(self):
    return reverse('blog:post_detail', args=[self.publish.year,
                                             self.publish.month,
                                             self.publish.day,
                                             self.slug])