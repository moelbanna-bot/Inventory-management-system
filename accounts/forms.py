from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
import re
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError


# Get the User model
user = get_user_model()

# Define role choices for the role field
role_choices = [
    ("manager", "Manager"),
    ("employee", "Employee"),
]


class UserRegisterForm(forms.ModelForm):  # Changed from UserCreationForm to ModelForm
    # Define form fields with required attributes
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)

    # Role field with choices and custom widget attributes
    role = forms.ChoiceField(
        choices=role_choices,
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        # Specify the model and fields to include in the form
        model = user
        fields = ("first_name", "last_name", "email", "username", "role")

    def clean_email(self):
        # Validate email uniqueness
        email = self.cleaned_data.get("email")
        # Exclude the current instance's email during updates
        filter_email = user.objects.filter(email=email)
        if self.instance.pk:
            filter_email = filter_email.exclude(pk=self.instance.pk)
        if filter_email.exists():
            raise forms.ValidationError("Email already exists")
        return email

    def clean_first_name(self):
        # Validate first name unchanged
        first_name = self.cleaned_data.get("first_name")
        pattern = r"^[A-Za-z]+$"
        if not re.match(pattern, first_name):
            raise forms.ValidationError("First name must contain only alphabets")
        if len(first_name) < 2 or len(first_name) > 10:
            raise forms.ValidationError(
                "First name must be between 2 and 10 characters"
            )
        return first_name

    def clean_last_name(self):
        # Validation unchanged
        last_name = self.cleaned_data.get("last_name")
        pattern = r"^[A-Za-z]+$"
        if not re.match(pattern, last_name):
            raise forms.ValidationError("Last name must contain only alphabets")
        if len(last_name) < 2 or len(last_name) > 10:
            raise forms.ValidationError("Last name must be between 2 and 10 characters")
        return last_name

    def clean_username(self):
        # Username validation fixed
        username = self.cleaned_data["username"]
        filter_username = user.objects.filter(username=username)
        if self.instance.pk:
            filter_username = filter_username.exclude(pk=self.instance.pk)
        pattern = r"^[a-zA-Z0-9_.-]+$"
        if not re.match(pattern, username):
            raise forms.ValidationError(
                "Username must contain only alphabets, numbers, and ._-"
            )
        if filter_username.exists():
            raise forms.ValidationError("Username already exists")
        return username

    def save(self, commit=True):
        # Role assignment unchanged
        user = super().save(commit=False)
        role = self.cleaned_data.get("role")

        if role == "manager":
            user.is_staff = True
        elif role == "employee":
            user.is_staff = False

        if commit:
            user.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not user.objects.filter(email=email).exists():
            raise ValidationError("This email address is not registered.")
        return email
