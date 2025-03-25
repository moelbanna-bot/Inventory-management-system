from django.shortcuts import render


# Permission check for admin users
# Only authenticated superusers have admin access
def is_admin(user):
    return user.is_authenticated and user.is_superuser


# Permission check for managers
# Only authenticated staff users have manager access
def is_manager(user):
    return user.is_authenticated and user.is_staff


# Permission check for regular employees
# Basic authenticated users have employee access
def is_employee(user):
    return user.is_authenticated


class RoleBasedPermissionMixin:
    # Placeholder for the permission check function
    test_func = None

    # Override the dispatch method to include permission check
    def dispatch(self, request, *args, **kwargs):
        if self.test_func:
            # If the user does not pass the permission check, render a 403 page
            if not self.test_func(self.request.user):
                return render(self.request, "403.html", status=403)
        # Call the parent class's dispatch method
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleBasedPermissionMixin):
    # Set the permission check function to is_admin
    test_func = is_admin


class ManagerRequiredMixin(RoleBasedPermissionMixin):
    # Set the permission check function to is_manager
    test_func = is_manager
