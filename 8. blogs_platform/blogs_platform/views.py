from blogs_platform.models import Post
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic.detail import DetailView
from blogs_platform.forms import PostForm, CommentForm
from hitcount.models import HitCount, HitCountMixin
from hitcount.views import HitCountDetailView


def index(request):
    name = request.GET.get('text', '')

    context = {'post_add_url': '/add_post'}

    posts_list = Post.objects.filter(status='v', subject__contains=name)
    html = 'index.html'

    if request.path == '/popular/':
        posts_list = Post.objects.filter(status='v', subject__contains=name).order_by("-hit_count_generic__hits")
        html = 'popular_index.html'

    elif request.path == '/last_added/':
        posts_list = Post.objects.filter(status='v', subject__contains=name).order_by('-id')
        html = 'last_added_index.html'

    paginator = Paginator(posts_list, 5)

    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context['posts'] = posts

    return render(request, html, context)


class PostsView(HitCountDetailView):
    model = Post
    template_name = 'post.html'
    count_hit = True  # Счетчик просмотров

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = context['post']

        context['comment_add_url'] = "/post/{}/add_comment".format(post.id)

        comments_list = post.comment_set.all()
        paginator = Paginator(comments_list, 5)

        page = self.request.GET.get('page')

        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)

        context['comments'] = comments

        return context


class PostAdd(CreateView):
    template_name = 'post_add.html'
    form_class = PostForm

    def get_success_url(self):
        return "/"


class CommentAdd(CreateView):
    template_name = 'comment_add.html'
    form_class = CommentForm

    def get_initial(self):
        return {
            "post": self.kwargs["post_pk"]
        }

    def get_success_url(self):
        return "/post/{}/".format(self.kwargs["post_pk"])
