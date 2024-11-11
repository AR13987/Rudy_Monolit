from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import UserProfileForm
from .models import Question, Choice, UserProfile, Vote
from django.utils.translation import gettext_lazy as _
from . import models

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.db.utils import IntegrityError
from django.contrib.auth.forms import AuthenticationForm
from .forms import QuestionForm



# Отображение списка последних опубликованных вопросов:
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.filter(
            pub_date__lte=timezone.now(),
            expiration_date__gt=timezone.now()
        ).order_by('-pub_date')[:5]



# Отображение подробной информации о выбранном вопросе, включая варианты ответов:
class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object

        if question.expiration_date < timezone.now():
            context['expired'] = True
        else:
            context['expired'] = False

        # Передаём объекты Choice и количество голосов:
        choice_votes = [(choice, choice.votes) for choice in question.choice_set.all()]
        context['choice_votes'] = choice_votes

        return context


# Отображение результатов голосования по выбранному вопросу:
class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'
    context_object_name = 'question'

    def get_object(self):
        question_id = self.kwargs.get('question_id')
        return get_object_or_404(Question, pk=question_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object

        choice_votes = [(choice.choice_text, choice.votes) for choice in question.choice_set.all()]
        context['choice_votes'] = choice_votes

        return context


@login_required
# Создание вопроса пользователем:
def create_question(request):
  if request.method == 'POST':
    form = QuestionForm(request.POST, request.FILES)
    if form.is_valid():
      question = form.save(commit=False)
      question.user = request.user
      question.save()

      choices = form.cleaned_data['choices']
      choice_list = [choice.strip() for choice in choices.split(',')]

      for choice_text in choice_list:
        Choice.objects.create(question=question, choice_text=choice_text)

      return redirect('polls:index')
  else:
    form = QuestionForm()
  return render(request, 'polls/create_question.html', {'form': form})


# Выход пользователя:
def logout_user(request):
    logout(request)
    return render(request,'polls/logout.html')


# Вход пользователя:
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('polls:index')
            else:
                form.add_error(None, 'Неверный логин или пароль.')
        else:
            # Ошибки в форме
            pass
    else:
        form = AuthenticationForm()
    return render(request, 'polls/login.html', {'form': form})



# Обработка голосования:
def vote(request, question_id):
  if not request.user.is_authenticated:
    return redirect('polls:login')

  question = get_object_or_404(models.Question, pk=question_id)

  if 'choice' in request.POST:
    try:
      choice_id = int(request.POST['choice'])
      selected_choice = question.choice_set.get(pk=choice_id)
    except (KeyError, Choice.DoesNotExist, ValueError):
      return render(request, 'polls/detail.html', {
        'question': question,
        'error_message': _("Выберите вариант ответа."),
      })
    else:
      try:
        Vote.objects.create(user=request.user, question=question, choice=selected_choice)
      except IntegrityError:
        return render(request, 'polls/detail.html', {
          'question': question,
          'error_message': _("Вы уже голосовали за этот вопрос."),
        })
      else:
        selected_choice.votes += 1
        selected_choice.save()

        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

  else:
    return render(request, 'polls/detail.html', {
      'question': question,
      'error_message': _("Выберите вариант ответа."),
    })



# Обработка регистрации нового пользователя:
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('polls:index')
    else:
        form = UserCreationForm()
    return render(request, 'polls/signup.html', {'form': form})



# Отображение профиля пользователя:
def profile(request):
    user = request.user
    user_profile = user.userprofile
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None
    return render(request, 'polls/profile.html', {'user_profile': user_profile})



# Редактирование профиля пользователя:
def edit_profile(request):
    user = request.user
    user_profile = user.userprofile

    profile_form = UserProfileForm(request.POST or None, request.FILES or None, instance=user_profile)

    if request.method == 'POST':
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')

        return redirect('polls:profile')

    return render(request, 'polls/edit_profile.html', {'profile_form': profile_form})



# Удаление профиля пользователя:
def delete_profile(request):
  user = request.user
  if request.method == 'POST':
    user.delete()
    return redirect('polls:index')
  return render(request, 'polls/delete_profile.html')