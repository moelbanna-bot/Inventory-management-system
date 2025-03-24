
# Permission check for admin users
# Only authenticated superusers have admin access
def is_admin(user):
    return user.is_authenticated and user.is_superuser

# Permission check for managers
# Only authenticated staff users have manager access
def is_manager(user):
    return user.is_authanticated and user.is_staff

# Permission check for regular employees
# Basic authenticated users have employee access
def is_employee(user):
    return user.is_authanticated