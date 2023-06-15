from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.views import LoginView, LogoutView
from accounts.forms import *

class SiteLoginView(LoginView):
    title = 'Авторизация'


class SiteLogoutView(LogoutView):
    title = 'Выход'


class SignUpView(generic.CreateView):
    title = "Регистрация"
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        # form.instance.user = self.request.user
        # form.save()
        print(form.fields)
        return super(SignUpView, self).form_valid(form)


# class UserSignUpView(generic.CreateView):
#     title = "Регистрация"
#     form_class = UserSignUpForm
#     success_url = reverse_lazy('login')
#     template_name = 'registration/signup.html'