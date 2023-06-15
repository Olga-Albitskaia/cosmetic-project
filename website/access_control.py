import functools

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from project import settings


class UserPassesTestOrganizationOrAdmin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user:
            if user.is_superuser:
                return True
            if not user.is_client():
                return True
        return False


def user_passes_test_admin(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.info(request, 'Доступ ограничен', 'alert alert-danger')
            return redirect(reverse('home'))
            # return HttpResponseForbidden()
        return func(request, *args, **kwargs)
    return wrapper


class UserPassesTestUserOrAdmin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user:
            if user.is_superuser:
                return True
            if user.user_type and user.user_type.id == 3:
                return True
        return False
