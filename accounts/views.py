from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.views import PasswordResetView, LoginView
from django.utils.crypto import get_random_string
from .forms import CustomPasswordResetForm
from .permissions import is_manager
from .utils import send_activate_email


def register(request):
    if not is_manager(request.user):
        return render(request, "403.html", status=403)
    print("checkpoint 1")
    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            try:
                user = form.save(commit=False)

                # generate a random password
                random_password = get_random_string(12)
                # Set the password
                user.set_password(random_password)
                # Now save the user
                user.save()

                # Send activation email with the generated password
                send_activate_email(request, user, random_password)

                messages.success(request, "Account created successfully")
                return redirect("home")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

    else:
        form = UserRegisterForm()

    return render(request, "accounts/register_user.html", {"form": form})


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "registration/password_reset_form.html"
    success_url = "../password_reset/done/"


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"

    def dispatch(self, request, *args, **kwargs):
        # If the user is already authenticated, redirect them
        if request.user.is_authenticated:
            # Redirect to your desired URL (home, dashboard, etc.)
            return redirect("home")

        # Otherwise, proceed with the normal login view
        return super().dispatch(request, *args, **kwargs)
