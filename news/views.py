from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .forms import PostForm
from .models import Post, PostCategory, Category
from datetime import datetime, timedelta
from .filters import PostFilter
from django.http import HttpResponse
from .tasks import send_message


class NewsList(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-published_date'
    template_name = 'news.html'
    context_object_name = 'news'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs


class DetailNews(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'
    queryset = Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_sub'] = not (self.request.user.username in Category.objects.all().values("subscribers"))
        return context

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)
        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)

        return obj


class NewsFilterList(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-published_date'
    template_name = 'news_search.html'
    context_object_name = 'news_search'
    paginate_by = 2

    def get_queryset(self):
        # Получаем обычный запрос
        queryset = super().get_queryset()
        # Используем наш класс фильтрации.
        # self.request.GET содержит объект QueryDict, который мы рассматривали
        # в этом юните ранее.
        # Сохраняем нашу фильтрацию в объекте класса,
        # чтобы потом добавить в контекст и использовать в шаблоне.
        self.filterset = PostFilter(self.request.GET, queryset)
        # Возвращаем из функции отфильтрованный список товаров
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset
        return context


class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'new_edit.html'


class PostCreate(LoginRequiredMixin, CreateView, PermissionRequiredMixin):
    permission_required = ('news.add_post',)
    form_class = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.choice = 'NW'
        return super().form_valid(form)


class ArticleCreate(LoginRequiredMixin, CreateView, PermissionRequiredMixin):
    permission_required = ('news.add_post',)
    form_class = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'article_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.choice = 'AR'
        return super().form_valid(form)


class PostDelete(LoginRequiredMixin, DeleteView, PermissionRequiredMixin):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts_list')


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
    return redirect('/')


class CategoryDetail(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'category.html'
    context_object_name = "cat"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = Category.objects.get(pk=self.kwargs['pk'])
        context['cat'] = category
        context['subs'] = category.subscribers.all()
        return context


@login_required
def subscribe(request, pk):
    category = Category.objects.get(pk=pk)
    category.subscribers.add(request.user.id)
    return redirect('/')
