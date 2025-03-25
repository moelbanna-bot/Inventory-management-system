from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activate_email(request, user, password):
    protocol = "https" if request.is_secure() else "http"
    domain = request.get_host()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    print(f"Sending email to: {user.email}")
    subject = "Welcome to our Inventory"
    plain_message = (
        "Welcome to our Inventory! Your account has been successfully created."
    )
    html_message = render_to_string(
        "accounts/emails/welcome.html",
        {
            "user": user,
            "protocol": protocol,
            "domain": domain,
            "uid": uid,
            "token": token,
            "password": password,
        },
    )
    from_email = "khaledgafaar211@gmail.com"
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
