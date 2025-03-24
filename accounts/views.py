from email.message import EmailMessage
from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.views import PasswordResetView
from .forms import CustomPasswordResetForm
from django.contrib.auth.decorators import user_passes_test
from .permissions import is_admin, is_manager, is_employee


def send_activate_email(request, user):
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    print(f"Sending email to: {user.email}")
    subject = 'Welcome to our Inventory'
    plain_message = 'Welcome to our Inventory! Your account has been successfully created.'
    html_message = render_to_string('accounts/emails/welcome.html', {'user': user,
                                                                     'protocol': protocol,
                                                                     'domain': domain,
                                                                     'uid': uid,
                                                                     'token': token,
                                                                     })
    from_email = 'khaledgafaar211@gmail.com'
    to_email = user.email

    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email: {e}")


@user_passes_test(is_manager, login_url='products_list')
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                send_activate_email(request, user)
                messages.success(request, 'Account created successfully')
                return redirect('home')
            except Exception as e:
                messages.error(request, 'An error occurred')


    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register_user.html', {'form': form})


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    success_url = '../password_reset/done/'
