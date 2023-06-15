from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class SignUpForm(UserCreationForm):
    def save(self, commit=True):
        instance = super(SignUpForm, self).save(commit=False)
        instance.user_type_id = 3;
        if commit:
            instance.save()
        return instance

    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2', 'last_name', 'first_name', 'middle_name', 'gender', 'birthday', 'email', 'phone', 'address')