# from django.contrib.auth.views import LoginView
# from django.shortcuts import redirect

# class CustomLoginView(LoginView):
#     def get_success_url(self):
#         user = self.request.user
#         if user.is_superadmin:
#             return '/admin-dashboard/'  # ou a URL que você quiser
#         elif user.warehouse:
#             return '/appointments/dashboard/'
#         else:
#             return '/'  # fallback


from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, reverse


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'  # <== agora está usando seu próprio template

    def get_success_url(self):
        if self.request.user.is_superadmin:
            return reverse('admin_dashboard')
        return reverse('appointment_list')    
        # return reverse('dashboard')
    # def get_success_url(self):
    #     user = self.request.user
    #     if user.is_superadmin:
    #         return '/admin-dashboard/'
    #     elif user.warehouse:
    #         return '/appointments/dashboard/'
    #     return '/'


