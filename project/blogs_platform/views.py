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

    posts = Post.objects.filter(status='v', subject__contains=name)

    if request.path == '/popular/':
        posts = Post.objects.filter(status='v', subject__contains=name).order_by("-hit_count_generic__hits")
        return render(request, 'popular_index.html', {"posts": posts})

    elif request.path == '/last_added/':
        posts = Post.objects.filter(status='v', subject__contains=name).order_by('-id')
        return render(request, 'last_added_index.html', {"posts": posts})

    return render(request, 'index.html', {"posts": posts})


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
