from django.shortcuts import render , get_object_or_404 
from .models import Post
from django.http import Http404 , HttpResponse
from django.core.paginator import Paginator , EmptyPage , PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
# Create your views here.

def post_list(request, tag_slug = None):
  post_list = Post.published.all()

  tag = None
  if tag_slug:
    tag = get_object_or_404(Tag, slug = tag_slug)
    post_list = post_list.filter(tags__in=[tag])


  #nno of post in one page is 3
  paginator = Paginator(post_list, 3)
  page_number = request.GET.get('page', 1)
  try:
    posts = paginator.page(page_number)
  except PageNotAnInteger:
    posts = paginator.page(1)
  except EmptyPage:
    posts = paginator.page(paginator.num_pages)
  return render(request , 'blog/post/list.html', {'posts': posts,'tag':tag})


def post_share(request , post_id):
  post = get_object_or_404(Post, id = post_id , status = Post.Status.PUBLISHED)
  sent = False

  if request.method == 'POST':
    form = EmailPostForm(request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      post_url = request.build_absolute_uri(post.get_absolute_url())
      subject = f"{cd['name']} recommends you read " f"{post.title}"
      message = f"Read {post.title} at {post_url}\n\n"\
                 f"{cd['name']}\'s comments: {cd['comment']}"
      send_mail(subject, message, 'marafay2610@gmail.com',[cd['to']])
      sent = True
  else:
      form = EmailPostForm()
  return render(request , 'blog/post/share.html' , {'post':post,'form':form,'sent':sent})


'''class Postlistview(ListView):
  queryset = Post.published.all()
  context_object_name = 'posts'
  paginate_by = 3
  template_name = 'blog/post/list.html','''


def post_detail(request, month, year, day, post):
  post = get_object_or_404(Post,
                           status = Post.Status.PUBLISHED,
                           slug = post,
                           publish__year = year,
                           publish__month = month,
                           publish__day = day)
  post_tags_ids = post.tags.values_list('id', flat=True)
  similar_posts = Post.published.filter(tags__in=post_tags_ids)\
                                .exclude(id=post.id)
  similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                              .order_by('-same_tags','-publish')[:4]
  return render (request , 'blog/post/detail.html' , {'post':post,'similar_posts': similar_posts})

