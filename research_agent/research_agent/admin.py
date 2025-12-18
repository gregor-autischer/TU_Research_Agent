from django.contrib.admin import AdminSite
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from functools import update_wrapper


class ResearchAgentAdminSite(AdminSite):
    site_header = 'Research Agent Administration'
    site_title = 'Research Agent Admin'
    index_title = 'Administration'

    def has_permission(self, request):
        """
        Return True if the user has permission to view the admin site.
        """
        return request.user.is_active and request.user.is_staff

    def admin_view(self, view, cacheable=False):
        """
        Decorator to wrap admin views.
        Shows custom access denied page for authenticated non-staff users
        instead of redirecting to login (which shows blank for logged-in users).
        """
        def inner(request, *args, **kwargs):
            # Check BEFORE calling super's admin_view to avoid CSRF issues
            if request.user.is_authenticated and not request.user.is_staff:
                return render(request, 'admin/access_denied.html', status=403)
            # Now call the parent's admin_view which includes CSRF protection
            wrapped_view = super(ResearchAgentAdminSite, self).admin_view(view, cacheable)
            return wrapped_view(request, *args, **kwargs)

        # Copy attributes from original view
        if not cacheable:
            inner = self._wrap_csrf(inner)
        return update_wrapper(inner, view)

    def _wrap_csrf(self, view):
        """Apply CSRF protection only if user is staff (will access admin)."""
        def wrapped(request, *args, **kwargs):
            # Skip CSRF for non-staff users since we just show access denied
            if request.user.is_authenticated and not request.user.is_staff:
                return view(request, *args, **kwargs)
            # Apply CSRF protection for staff users
            return csrf_protect(view)(request, *args, **kwargs)
        return wrapped


# Create custom admin site instance
admin_site = ResearchAgentAdminSite(name='admin')
