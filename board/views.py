from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from datetime import datetime
from pprint import pprint
from .models import Post, Category, Reply
from .filters import PostFilter
from .forms import PostForm, ReplyForm
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View


#Создаем свои классы, которые наследуются от ListView и DetailView.
class PostList(ListView):
    model = Post
    ordering = '-time_of_creation'
    template_name = 'post_list.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset
        pprint(context)
        return context

# Добавляем новое представление для поиска постов.
class PostSearch(ListView):
    model = Post
    ordering = '-time_of_creation'
    template_name = 'post_search.html'
    context_object_name = 'post_search'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post_detail'


# Добавляем новое представление для создания постов.
class PostCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('post_list')
    permission_required = ('board.add_post')

# Добавляем представление для изменения постов.
class PostUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('post_list')
    permission_required = ('board.change_post')

# Представление, удаляющее пост.
class PostDelete(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    permission_required = ('board.delete_post')



class CategoryListView (ListView):
    model = Post
    template_name = "category_list.html"
    context_object_name = "category_post_list"


    def get_queryset(self):
        self.category = get_object_or_404(Category,id=self.kwargs['pk'])
        queryset = Post.objects.filter(categories=self.category).order_by('-time_of_creation')
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_not_subscriber"] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context

class ReplyAdd(CreateView):
    form_class = ReplyForm
    model = Reply

    template_name = 'reply_add.html'
    context_object_name = 'reply_create'

    success_url = '/posts/'

    def form_valid(self, form):
        reply = form.save(commit=False)
        reply.author = self.request.user
        reply.post = get_object_or_404(Post, id=self.kwargs['pk'])
        form.save()
        return redirect('post', reply.post.pk)

class Replies(ListView):
    model = Reply
    template_name = 'replies.html'
    context_object_name = 'replies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        replies_to_author = Reply.objects.filter(post__post_author=self.request.user)
        context['replies_to_author'] = replies_to_author
        return context


    def delete_reply(self, pk):
        reply = Reply.objects.get(id=pk)
        reply.delete()
        return redirect('/posts/')


    def allow_reply(self, pk):
        reply = Reply.objects.get(id=pk)
        reply.is_allowed = True
        return redirect('/posts/')


class VerifyCodeView(View):
    template_name = 'verify_code.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        entered_code = request.POST.get('one_time_code')
        stored_code = request.session.get('one_time_code')

        if entered_code == stored_code:
            # If the code matches, proceed with user registration
            user = User.objects.get(username=request.session.get('register_username'))
            user.set_password(request.session.get('register_password'))  # Set the actual password
            user.save()

            # Log in the user
            login(request, user)

            # Clear the session data
            del request.session['one_time_code']
            del request.session['register_username']
            del request.session['register_password']

            return redirect('home')

        return render(request, self.template_name, {'error_message': 'Неверный код'})


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    message = "Вы подписались на рассылку по категории"
    return render(request, 'subscribe.html', {'category': category, 'message': message})